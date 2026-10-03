# Auditoria de identidade da experiência — o egresso diante do Ifes

Data: 2026-10-02 · Base: `main` em `4c5354e` (após a Feature 013)

Nada foi implementado; este documento é só o diagnóstico. Complementa a
[auditoria de UX da 008](2026-10-01-ux-feature-008.md), que tratou usabilidade. Aqui a
pergunta é outra: **a experiência transmite "o Ifes já conhece parte da sua história e
quer saber como ela continuou", ou "preencha um questionário institucional"?**

## Método

- Interface real em banco local dedicado (`trajetoria_identidade`), preparado com
  `preparar_demonstracao` e servido com `TRAJETORIA_DEMONSTRACAO=1`; só dados fictícios.
- Viewport 375×812 (celular) em toda a passagem.
- Pessoas fictícias escolhidas pela riqueza de trajetória:
  - **Diego**: Técnico em Química (Integrado, 2012) → Licenciatura em Química (2017) →
    Mestrado Profissional em Química (2020), todos no campus Vila Velha. Jornada completa
    pela Licenciatura, com Q33 = Sim e Q46 = Não.
  - **Maria**: Tecnologia em Análise e Desenvolvimento de Sistemas (Serra, 2022) e
    Especialização em Informática na Educação (Cefor, a distância, 2025). Tela de escolha.
- Cada achado e cada recomendação passaram pelas duas perguntas da lente:
  - **(P1)** Isto facilita genuinamente a resposta no celular?
  - **(P2)** Isto faz sentido especificamente para uma pessoa que retoma sua relação com o
    Ifes como egresso?

  Uma solução que só passa em P1 é tratada como genérica demais.

## 1. Resumo executivo

- **Hoje a jornada diz "preencha um questionário".** O primeiro conteúdo depois do termo
  é um censo de 8 perguntas pessoais. O título de toda Seção é "Egresso Ifes". As Seções
  classificam a pessoa em terceira pessoa ("Egresso que trabalha"). O fim é "Este
  formulário chegou ao fim!".
- **O Ifes mostra que sabe e, em seguida, pergunta.** A linha "Licenciatura em Química ·
  Vila Velha · 2017" fica logo acima de "Em que ano você concluiu…?" e "Em qual campus…?".
  Nenhum texto conserta essa contradição; ela depende da decisão pendente DP-307.
- **O Ifes ignora o que sabe sobre o "depois".** Diego responde "Após o curso, você: Fiz
  mestrado" sobre um mestrado que o próprio Ifes registra e lista na tela de formações. É
  a oportunidade mais forte e mais legítima de personalização: dado real, da relação
  histórica, e que reduz a carga de memória.
- **A trajetória aparece como pendências.** As três formações de Diego, uma continuidade
  de oito anos no mesmo campus e na mesma área, aparecem como três fichas iguais, cada
  uma com uma situação de pesquisa ("Sem pesquisa disponível no momento").
- **A matéria-prima é menor do que o desejável, e isso é um limite saudável.** Hoje a
  instituição conhece curso, unidade, nível, modalidade, forma de oferta, ano ou data de
  conclusão e as outras formações. Não conhece ingresso, projetos, bolsas nem "história
  do período". A identidade deve ser construída com o que existe, sem simular o resto
  (seção 2).

## 2. O que o Ifes realmente sabe — inventário da matéria-prima

Personalizar com dado real exige saber qual dado é real. Elementos sugeridos para a
lente, confrontados com o contrato da fonte acadêmica
(`trajetoria/fonte_academica/contrato.py`) e com a Constituição (Princípio III):

| Elemento da relação | Origem | Disponível hoje | Uso recomendado |
|---|---|---|---|
| Formação realizada | Institucional (001) | Sim: curso, nível, modalidade, forma de oferta | Âncora de toda a jornada |
| Campus | Institucional | Sim (`unidade`) | Idem; também é referência de Q40 |
| Período em que estudou | Institucional | **Parcial**: só o ano ou a data de **conclusão**; não há ingresso no contrato (DP-702 já cita "período de ingresso") | Falar em "concluiu em 2017"; **não** escrever "estudou de 2013 a 2017" |
| Outras formações no Ifes | Institucional | Sim (`Pessoa.conclusoes`, em ordem de ano) | Trajetória (ID-03) e continuidade dos estudos (ID-02) |
| Ensino, pesquisa, extensão, monitoria, IC, bolsas | Perguntado (Q22–Q32); candidato a institucional (inventário O-11), **sem fonte** | Não | Manter declarado; não simular "você participou de…" |
| Continuidade dos estudos | **No Ifes**: institucional (outras conclusões); **fora**: declarado | Parcial | ID-02 |
| Trajetória profissional | Declarado | Não | Nunca presumir |
| Tempo desde a conclusão | Derivado (ano de conclusão × momento da Participação) | Calculável | Pode ser exibido como derivado; nunca gravado como resposta |
| Relação atual com o Ifes | Q29 (declarada); Participações anteriores (domínio do NIAE) | Sim no domínio, **escondido na tela** (D-3) | ID-10 |
| Geração/coorte | Derivado (curso + campus + ano) | Calculável | Só implícito ("em 2017"); sem comparação com colegas |
| História institucional do período | Nenhuma fonte; notícias e eventos ficam fora da fronteira (Princípio VI) | Não | **Não usar** (seção 5) |

## 3. Narrativa atual, tela a tela

| Tela | O que diz hoje (implicitamente) | Efeito sobre a relação |
|---|---|---|
| Formações / início | "Sua pesquisa"; "Esta pesquisa refere-se à sua formação:" + ficha | O objeto é a pesquisa, não a pessoa |
| Escolha (Maria) | "Sobre qual formação do Ifes você responderá esta pesquisa?" | Escolha de tarefa, não "encontramos estas formações" |
| Seção 1 | H1 "Egresso Ifes"; "Prezado(a) egresso(a)… Basta que você responda a este questionário!" | Carta genérica, quando o curso, o campus e o ano já estão na tela |
| Seção 2 | 8 perguntas pessoais obrigatórias, a primeira tela de conteúdo | Cadastro antes de qualquer interesse pela história |
| Seções 3 e 6 | Contexto acima, a mesma informação perguntada abaixo (lista de 50 cursos) | Contradiz a mensagem central |
| Seção 8 "Avaliação" | 10 lembranças "durante o curso", um vínculo atual e, no fim, "Atualmente você trabalha?" | Passado e presente misturados sob um rótulo de avaliação |
| Seções 9 a 12 | "Egresso que trabalha", "Estudo", "Egresso que estuda" | A pessoa é classificada |
| Seção 13 | Sem título; "O meu curso no Ifes mudou a minha vida…" | O momento mais pessoal é o mais anônimo |
| Conclusão / confirmação | "Pesquisa concluída. Obrigado…" + ficha + "Este formulário chegou ao fim!" | Fecha o formulário, não a conversa |
| Formações depois | "Não há pesquisa pendente para você neste momento." | Caixa de tarefas zerada |

## 4. Achados priorizados

Natureza de cada achado: **[I]** interface (template, texto fixo; a linguagem definitiva é
DP-801); **[V]** conteúdo da Versão (instrumento; Princípio XIII, exige nova Versão e
decisão da CPAEG); **[D]** decisão de domínio ou institucional pendente.

### ALTO

**ID-01 — "Mostrar e depois perguntar" (Q10–Q19) [D]**

- **Evidência:** Seção 3 de Diego. "Sobre a sua formação: Licenciatura em Química · Vila
  Velha · 2017" e, logo abaixo, "Em que ano você concluiu o seu curso no Ifes?", "Em
  qual campus…" (lista de 23), modalidade, nível ("Indique o questionário que pretende
  preencher"). Depois, a Seção 6 pede o curso numa lista de 50.
- **Lente:** P1 — 5 a 6 respostas desnecessárias, duas delas em listas longas. P2 — é o
  ponto exato em que "o Ifes conhece sua história" vira "o Ifes não sabe quem você é".
  Nenhuma microcopy compensa isso.
- **Recomendação:** levar DP-307 à CPAEG como a decisão de maior alavanca da identidade
  da experiência. Até lá, a interface não pode agir: o FR-028 da 008 proíbe
  pré-preencher, sugerir, ocultar ou pular. **Não** recomendo um texto que justifique a
  repetição ("estas perguntas repetem…"): ele institucionaliza a contradição.
- **Pertence a:** 003/DP-307 (já registrado como D-1 na auditoria anterior).

**ID-02 — A continuidade dos estudos no Ifes é conhecida e ignorada [D + I]**

- **Evidência:** Diego, Seção "Estudo": "Após o curso, você: … Fiz mestrado". O Mestrado
  Profissional em Química (Vila Velha, 2020) está na lista de formações dele. Maria,
  respondendo sobre TADS (2022), passaria pelo mesmo com a Especialização do Cefor
  (2025).
- **Lente:** P1 — menos esforço de memória e de classificação ("lato sensu?"). P2 — é
  literalmente "encontramos esta formação na sua trajetória", com dado real, e só faz
  sentido para quem tem história no Ifes. Passa nas duas.
- **Recomendação:** na Seção que trata dos estudos, exibir como **contexto
  institucional**, separado das Perguntas: "No Ifes, depois desta formação, você também
  concluiu: Mestrado Profissional em Química — Vila Velha, 2020." Sem marcar opção alguma.
  Q47 continua declarada, porque cobre também estudos fora do Ifes. Uma divergência entre
  o declarado e o institucional é tratada na análise, como no
  [ADR 0003](../adr/0003-q14-resposta-declarada.md).
- **Por que [D]:** exibir contexto *ao lado* de uma Pergunta específica pode ser lido
  como "sugerir" ou "destacar" (FR-028), e mostrar outra formação dentro de uma
  Participação amplia o que é apresentado ao egresso (DP-702). Precisa de decisão
  explícita, não de interpretação do desenvolvimento.

**ID-03 — A tela de formações é uma caixa de pendências, não uma trajetória [I]**

- **Evidência:** Diego depois de concluir: "Suas formações / Não há pesquisa pendente
  para você neste momento.", seguido de três fichas de 5 ou 6 linhas cada, com
  "Sem pesquisa disponível no momento." e "A pesquisa referente a esta formação não está
  disponível neste momento." em duas delas. A continuidade 2012 → 2017 → 2020 no mesmo
  campus só se percebe lendo três fichas inteiras.
- **Lente:** P1 — três fichas de 5 ou 6 linhas viram três linhas; a ação fica visível
  na primeira tela. P2 — a pessoa vê a própria passagem pelo Ifes em ordem, com dados
  que a instituição de fato tem.
- **Recomendação:** título "Sua trajetória no Ifes". Uma linha por formação, em ordem
  cronológica (o modelo já ordena por ano de conclusão): "2012 · Técnico em Química
  (Integrado) · Vila Velha". A situação da pesquisa aparece só quando há algo a fazer ou
  já feito (ver ID-11). Sem linha do tempo gráfica, setas, selos ou percentuais.
  **Não** rotular a sequência ("verticalização"); isso é leitura analítica, não fato a
  mostrar.
- **Pertence a:** 008 (apresentação); não muda a regra da 007.

### MÉDIO

**ID-04 — A entrada fala da pesquisa, não da pessoa [I]**

- **Evidência:** "Sua pesquisa / Esta é a pesquisa do Ifes com seus egressos… / Esta
  pesquisa refere-se à sua formação:" e a ficha.
- **Recomendação:** abrir com o fato e a pergunta: "Você concluiu Licenciatura em
  Química no campus Vila Velha em 2017. O Ifes quer saber como sua trajetória seguiu
  depois disso." Logo em seguida, a frase operacional que já existe (seção por seção,
  pode parar e continuar). Ficam só os atributos informados pela fonte (FR-026 da 008):
  sem ano, a frase omite o ano; não se inventa nada.
- **Lente:** P1 neutro (mesma altura); P2 forte.

**ID-05 — Rótulos de categoria em vez de relação [I + V]**

- **Evidência:** H1 "Egresso Ifes" (título do instrumento) em toda Seção (UX-07 da
  auditoria anterior continua aberto). Títulos de Seção: "Egresso que trabalha",
  "Egresso que não trabalha", "Egresso que estuda", "Avaliação".
- **Recomendação:** [I] título da Seção como heading principal (UX-07). [V] na próxima
  Versão, propor à CPAEG títulos em segunda pessoa e no tempo certo, por exemplo "Seu
  trabalho hoje", "Seus estudos depois do curso", "Lembranças do curso". Se isso é
  correção editorial ou exige nova Versão depende da política de versionamento (inventário
  O-4).

**ID-06 — "Durante o curso" sem dizer qual curso nem quando [I]**

- **Evidência:** Seção 8: 11 perguntas sobre "durante o curso" e "o curso" ("Você mantém
  algum vínculo com o curso…"). Para Diego, com três cursos no mesmo campus, "o curso"
  pode ser qualquer um; a única âncora é "Sobre a sua formação: …" no topo.
- **Lente:** P1 — a pessoa não precisa voltar ao topo para lembrar; uma linha. P2 —
  egressos com mais de uma formação são comuns no Ifes (Integrado → graduação →
  pós-graduação); é um problema próprio deste domínio.
- **Recomendação:** quando a Pessoa tem mais de uma formação, a linha compacta diz
  explicitamente sobre o que se responde: "Você está respondendo sobre: Licenciatura em
  Química · Vila Velha · 2017". Não alterar o texto das Perguntas (Versão).

**ID-07 — A jornada começa por um cadastro [V]**

- **Evidência:** depois do termo, a primeira tela é sexo/identidade de gênero, idade,
  raça/cor, PcD, deficiência, estado civil, escolaridade do pai e da mãe: 8 perguntas, 7
  obrigatórias. A história ("o que aconteceu depois") só começa no fim da Seção 8, com Q33.
- **Recomendação:** registrar como **oportunidade metodológica futura** (Princípio XIII),
  não como correção: uma ordem formação (contexto) → depois (trabalho, estudos) →
  durante (lembranças) → impactos → perfil. Mudar a ordem afeta comparabilidade e efeito
  de ordem, por isso é decisão da CPAEG, com nova Versão. Q3 (idade) é derivável se
  houver data de nascimento institucional (inventário).

**ID-08 — O texto de abertura é uma carta genérica [V]**

- **Evidência:** "Prezado(a) egresso(a) do Ifes" … "Basta que você responda a este
  questionário!", com o curso, o campus e o ano visíveis logo acima.
- **Recomendação:** a personalização vem da interface (ID-04), antes do texto da Versão.
  **Não** introduzir campos variáveis ("{curso}") nos textos do instrumento: isso
  transforma o editor em motor de templates (Princípio XXIII) e mistura dado
  institucional com texto versionado. Numa próxima Versão, a abertura pode falar de
  continuidade ("queremos saber como sua trajetória seguiu") sem nomear dados.

**ID-09 — O encerramento fecha um formulário, não uma conversa [I]**

- **Evidência:** "Pesquisa concluída / Obrigado pela sua participação." + ficha +
  "Este formulário chegou ao fim! / Agradecemos imensamente…" (agradecimento em dobro,
  UX-18 ainda aberto).
- **Recomendação:** uma frase que nomeia o que foi registrado e para quê, dentro da
  finalidade do termo: "Suas respostas sobre a Licenciatura em Química foram
  registradas. Elas ajudam o Ifes a entender o caminho de quem se forma aqui."
  Se houver outra formação com pesquisa disponível, oferecê-la ali mesmo. **Não**
  prometer novo contato nem "daqui a X anos" (Princípio IX; periodicidade é da Proex/Proen).

**ID-10 — A relação com o Ifes perde a memória [D]**

- **Evidência:** auditoria anterior, D-3: encerrada a Campanha, quem respondeu passa a
  ver "Sem pesquisa disponível no momento". No ciclo longitudinal, quem volta numa nova
  Campanha não vê que já respondeu antes.
- **Lente:** P2 forte. "Você respondeu sobre esta formação em 2025" é o reconhecimento
  mais honesto de uma relação contínua e usa só dado do próprio NIAE.
- **Recomendação:** decidir (regra da 007) se Participações concluídas em Campanhas
  encerradas aparecem na trajetória, só com a data e **nunca** com as respostas (DP-802).
  Só então "bem-vindo(a) de volta" passa a ser verdadeiro.

### BAIXO

- **ID-11 [I]:** situações negativas repetidas por formação ("Sem pesquisa disponível no
  momento", "…não está disponível neste momento") ocupam a trajetória com o que não
  existe. Omitir quando não há nada a fazer; manter "Pesquisa já respondida" e "Pesquisa
  em andamento".
- **ID-12 [I]:** a mesma lista mistura "Ano de conclusão 2022" e "Data de conclusão
  28/03/2025" (Maria). Na linha da trajetória, usar o ano para todas; a data completa não
  acrescenta nada à identificação.
- **ID-13 [V]:** a Seção 13, sobre impacto na vida ("mudou a minha vida para melhor"),
  não tem título (UX-11). Propor um título descritivo na próxima Versão, por exemplo
  "Impactos da formação" (nome que o inventário já usa), sem tom emocional.
- **ID-14 [I]:** a tela de escolha (Maria) começa por "Sobre qual formação do Ifes você
  responderá esta pesquisa?". Melhor partir do que foi encontrado: "Encontramos duas
  formações suas no Ifes. Cada uma tem sua própria pesquisa; escolha por qual começar."
  No celular, o primeiro botão fica abaixo da dobra; com ID-03, as duas opções cabem na
  primeira tela.

## 5. O que não fazer

Cada item abaixo falha em P2, viola um princípio ou é o excesso que a lente pede para
evitar.

| Tentação | Por que não |
|---|---|
| "Em 2017, o campus Vila Velha…": fatos históricos do período | Não há fonte no domínio; notícias e eventos são externos (Princípio VI); é o caminho direto para a nostalgia artificial e para o erro factual |
| "Sua turma de 2017", "X% dos seus colegas já responderam" | Comparação social e exposição de agregados a quem responde; pressão, não relação |
| Selos, progresso percentual, "complete seu perfil", sequências | Gamificação; indicador de progresso, percentual e estimativa de tempo foram excluídos de propósito (FR-095). Orientação de percurso é outra coisa (seção 6) |
| Marcar respostas a partir do dado institucional | Princípio III e FR-028; dado institucional não é declaração |
| Campos variáveis no texto da Versão | Princípio XXIII (editor não é form builder); quebra a preservação histórica do texto |
| Uma pergunta por tela, ao estilo conversa | Padrão comercial; multiplica telas (Princípio XIV) e não é específico do Ifes; a 008 funciona sem JS. O meio-termo são blocos curtos (seção 6), não página única nem dezenas de telas |
| "Bem-vindo(a) de volta" na primeira Participação | Afirma uma relação com o sistema que ainda não existe; só depois de ID-10 |
| Saudação pelo nome como principal recurso de personalização | O nome é só apresentação (001), pode faltar, e sem autenticação real não deve criar falsa intimidade; não substitui contexto da formação |
| Fotos, marca ou cores por campus | Identidade visual é DP-801; personalização cosmética passa em P1 e não diz nada da história |

## 6. Arquitetura narrativa recomendada

O objetivo não é reescrever o instrumento, e sim alinhar cada camada que pode mudar sem
decisão metodológica.

```
"O que o Ifes sabe"          "O que aconteceu depois"        "Olhando para trás"        "Sobre você"
 trajetória (ID-03)    →      trabalho, estudos         →     lembranças do curso   →    perfil
 entrada (ID-04)              + contexto de ID-02              + âncora de ID-06           (ID-07)
 [I agora]                    [D]                             [I agora]                   [V futuro]
```

- **Agora, só interface (sem decisão nova, dentro do FR-028 e do tratamento provisório
  de DP-801):** ID-03, ID-04, ID-06, ID-09, ID-11, ID-12, ID-14, e UX-07/UX-18 da
  auditoria anterior.
- **Pacote de decisão para a CPAEG, "o que o Ifes mostra e deixa de perguntar":** DP-307
  (ID-01), exibição de outras formações como contexto na Participação (ID-02, DP-702) e
  histórico de Participações na trajetória (ID-10, D-3).
- **Próxima Versão do instrumento (oportunidade metodológica explícita):** títulos de
  Seção (ID-05, ID-13), ordem da jornada (ID-07) e texto de abertura (ID-08).

### Orientação de percurso, transições e tamanho dos blocos

Progresso quantitativo não é o mesmo que orientação de percurso. "67% concluído" ou
"faltam 5 minutos" estão vedados (FR-095) e, com ramificações, seriam imprecisos. Uma
frase como "Agora: sua situação hoje" não mede nada: diz onde a pessoa está. Isso é
navegação e cabe na experiência, com três condições:

- **Só o que é verdade em todos os percursos.** O bloco seguinte depende de Q33 e Q46.
  "A seguir: …" só pode anunciar o que nenhum ramo altera. Na ordem atual do
  instrumento, o exemplo "Depois: sua experiência no Ifes" seria falso, porque as
  lembranças do curso (Seção 8) vêm *antes* de trabalho e estudos. A orientação por
  momentos ("depois → olhando para trás → sobre você") pressupõe a reordenação de ID-07.
- **Do conteúdo da Versão, não de um mecanismo novo.** A Seção já tem título e texto
  próprios, exibidos no topo da página (`secao.html`). Uma transição como "Olhando para
  trás. As próximas perguntas são sobre a sua experiência durante o curso." é texto de
  Seção, sem tela intermediária, modelo de "etapas" nem agrupamento novo (FR-096;
  Princípio XXIII). Por isso é [V]: entra numa revisão da Versão, não no polish.
- **Sem telas de respiro.** A pausa acontece na troca de Seção, que já é uma nova página.
  Uma tela só para respirar acrescenta um toque e um carregamento no celular, sem
  acrescentar conteúdo.

**Blocos curtos** são o meio-termo entre a página longa e "uma pergunta por tela". Hoje
o problema é o tamanho de algumas Seções, não o paradigma: a Seção 8 tem 14 perguntas
(cerca de 3.900 px em 375 px de largura) e mistura lembranças com "Atualmente você
trabalha?"; a Seção 9 tem 11. Dividir uma Seção é mudança de Versão [V]. Paginar dentro
de uma Seção pela interface exigiria guardar posição de jornada e criaria um mini-wizard
(FR-096), além de conflitar com a regra de que a ramificação vale ao sair da Seção.

### Exemplos de microcopy

Exemplos conceituais. A linguagem definitiva é DP-801. Todo dado citado vem da Conclusão
Acadêmica ou da Participação; nenhum é deduzido.

| Onde | Hoje | Exemplo | Dado usado |
|---|---|---|---|
| Título da tela de formações | Sua pesquisa / Suas formações | Sua trajetória no Ifes | — |
| Entrada | Esta pesquisa refere-se à sua formação: | Você concluiu Licenciatura em Química no campus Vila Velha em 2017. O Ifes quer saber como sua trajetória seguiu depois disso. | curso, unidade, ano |
| Escolha | Sobre qual formação do Ifes você responderá esta pesquisa? | Encontramos duas formações suas no Ifes. Cada uma tem sua própria pesquisa; escolha por qual começar. | contagem de formações elegíveis |
| Contexto nas Seções (várias formações) | Sobre a sua formação: … | Você está respondendo sobre: Licenciatura em Química · Vila Velha · 2017 | curso, unidade, ano |
| Seção de estudos (após decisão) | — | No Ifes, depois desta formação, você também concluiu: Mestrado Profissional em Química — Vila Velha, 2020. | outras conclusões posteriores |
| Confirmação | Pesquisa concluída. Obrigado pela sua participação. | Suas respostas sobre a Licenciatura em Química foram registradas. | curso |
| Retorno (após ID-10) | Sem pesquisa disponível no momento. | Você respondeu sobre esta formação em 2025. | data da Participação concluída |

## 7. O que esta auditoria não avaliou

Esta auditoria tratou da identidade da experiência e da relação entre o egresso e o Ifes.
**Ela não substitui** a [auditoria de usabilidade da 008](2026-10-01-ux-feature-008.md) e
**não encerra** a experiência mobile: ergonomia de interação, interrupção e retomada,
teclado virtual, componentes de resposta em telas estreitas, conectividade,
acessibilidade móvel e instrumentação de abandono ficam para uma auditoria própria.
Passar a jornada a 375 px aqui serviu para ler a narrativa no tamanho real, não para
avaliar ergonomia.

Para orientar essa auditoria, os temas se dividem assim:

| Situação | Temas |
|---|---|
| Já observados, em parte, na auditoria da 008 | Erros e validação (UX-01, UX-12); tamanhos de toque; escalas 1–5 em 320 px; rolagem horizontal; foco e teclado físico; viewports de 320 a 1280 px |
| Não avaliados e testáveis hoje com a demonstração | Interrupção e retomada no meio de uma Seção (UX-04 só tratou o aviso); teclado virtual sobre campos e botões; uso com uma mão (alcance de "Salvar e continuar", "Voltar", "Sair"); conexão lenta ou perdida ao salvar; leitor de tela no celular (TalkBack, VoiceOver); zoom e fonte ampliada do sistema; comportamento em navegador embutido de aplicativo |
| Dependem de decisão pendente antes de serem auditáveis | Abertura a partir de WhatsApp ou e-mail (forma de acesso e identificação: 004/DP-406); analytics de abandono (DP-803); retrato pós-resposta, cópia das próprias respostas e compartilhamento (DP-802) |

O último grupo não é lacuna de auditoria: sem a decisão, não há o que observar, e
qualquer tela desenhada antes dela cristalizaria uma hipótese (Princípio XXIX). Um
"retrato" compartilhável, em particular, precisa passar pelos mesmos filtros da seção 5
(exposição de dados, comparação social, gamificação) antes de virar proposta.

## 8. Recomendação de próximo passo

1. **Polish de identidade da 008, só interface:** ID-03, ID-04, ID-06, ID-09, ID-11,
   ID-12 e ID-14. Pequeno, em template, texto fixo e `apresentacao.py`, sem modelo novo.
   É o que mais muda a sensação da jornada no celular sem depender de ninguém.
2. **Levar à CPAEG um único pacote de decisão** com DP-307, a exibição de outras
   formações (DP-702) e o histórico de Participações (D-3). ID-01 e ID-02 sozinhos valem
   mais que todo o resto deste documento.
3. **Registrar ID-05, ID-07, ID-08 e ID-13**, junto com as transições por texto de Seção
   e a divisão das Seções longas (seção 6), como insumo da primeira revisão explícita do
   instrumento, sem alterar a Versão atual.
4. **Fazer a auditoria mobile-first à parte**, a partir do segundo grupo da seção 7, e
   deixar o terceiro grupo esperando as decisões de que depende.
