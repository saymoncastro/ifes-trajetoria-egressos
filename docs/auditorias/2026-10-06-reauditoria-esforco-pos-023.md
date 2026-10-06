# Reauditoria objetiva do esforço de preenchimento (pós-Feature 023)

Data: 2026-10-06 · Base: `main` em `ced455f` (Feature 023 integrada, PR #38)

Esta reauditoria repete a medição da
[auditoria de esforço de 2026-10-05](2026-10-05-auditoria-esforco-preenchimento.md) depois da
[Feature 023](../../specs/023-jornada-menos-esforco/spec.md). Ela usa os mesmos cenários, as
mesmas métricas e o mesmo aparelho emulado. Não propõe nova estratégia: verifica o que mudou,
o que ainda custa esforço e onde está o próximo ganho. Nada foi implementado.

## Método

- **Ambiente:** banco de demonstração recriado do zero (`preparar_demonstracao`), servidor
  local, navegador do app com viewport de 375×812 (celular).
- **Execução:** a pessoa fictícia entra digitando CPF e data, responde as obrigatórias como
  um egresso faria e envia cada parte. Um script mede cada tela antes do envio: altura total,
  posição da primeira pergunta, perguntas apresentadas e obrigatórias, toques necessários
  (rádio ou escala = 1; lista = 2; caixa = 1; texto = 2 + teclas; envio = 1).
- **Interrupção:** recarregar no meio de uma parte; expirar a sessão (inatividade reduzida a 1
  minuto só para o teste) e entrar de novo digitando os dados; "Salvar e sair" e retomada do
  declarante.
- **Cenários:**
  - **A**, Ana: TADS, trabalha, não estuda (o mesmo da auditoria);
  - **B**, Fernanda: técnico subsequente, não trabalha, estuda, usa "Outro" com descrição;
  - **C**, declarante fora da base: não confirmado, informa a formação, usa "Corrigir";
  - **várias formações**, Diego: conclui uma e segue para a próxima.
- **Evidências:** [`evidencias-reauditoria-023/`](evidencias-reauditoria-023/).

## 1. Resultado em uma frase

**A 023 eliminou o trabalho desperdiçado que se propôs a eliminar e não mexeu no trabalho
estrutural, como era previsto.** O ganho foi real: zero perdas silenciosas, zero erros de
forma no caminho, horizonte em todas as telas e passagem direta para a próxima formação. A
quantidade de trabalho, porém, ficou praticamente igual (46 perguntas, ~61 toques, ~25
teclas). O que sobra de esforço evitável está quase todo no instrumento.

## 2. Orçamento de interação: antes × medido

### Cenário A (Ana)

| Métrica | Antes (auditoria) | Projetado A+B | **Medido após 023** |
|---|---:|---:|---:|
| Telas (carregamentos) | 12 | 12 | **12** |
| Perguntas apresentadas | 46 | 46 | **46** (42 obrigatórias) |
| Campos digitáveis obrigatórios | 4 | 4 | **4** |
| Teclas | ~25 | ~25 | **~25** |
| Toques | ~62 | ~60 | **~61** |
| Rolagem (telas de 812 px) | 27,6 | ~24 | **25,7** |
| Primeira pergunta da parte 1 | 1,73 tela | — | **1,17 tela** |
| Erros de forma possíveis no caminho | 2 | 0 | **0** |
| Ação principal da confirmação visível sem rolar | não | sim | **sim** (a 488 px) |
| Indicação de quanto falta | nenhuma | em toda parte | **em toda parte** |

Alturas medidas, em px: Termos 1 382 · Pessoais 2 647 · Curso 1 880 · Graduação 964 ·
Avaliação 3 730 · Trabalha 4 366 · Estudo 1 773 · Parte 8 1 650 · Concluir 1 393 · Concluída
1 099.

### Cenário B (Fernanda)

| Métrica | Antes | **Medido** |
|---|---:|---:|
| Perguntas | 40 | **40** |
| Telas | 13 + 1 reapresentação por erro | **13**, sem reapresentação |
| Toques | ~66 | **~62** |
| Teclas | ~60 | **~51** |
| Rolagem | ~28 (incl. ~5 de volta ao erro) | **24,3** |

O "Outro" com descrição, que antes provocava a recusa da Seção mais longa, passou sem erro: o
campo só aparece com a opção marcada.

### Cenário C (declarante)

| Métrica | Antes | **Medido** |
|---|---:|---:|
| Decisão "Conferir × Informar" | sem critério | **dois passos numerados** ([04](evidencias-reauditoria-023/04-nao-confirmada-dois-passos.jpg)) |
| Toques até a parte 1 | ~14 | **~15** (o nível virou rádio; o resto igual) |
| Teclas até a parte 1 | ~59 | **~59** |
| Corrigir a declaração | voltar pelo navegador | **1 toque, campos preservados** |
| Dados informados duas vezes | 4 | **4** (curso, unidade, nível, ano; [07](evidencias-reauditoria-023/07-declarada-repeticao-s3.jpg)) |
| Total até concluir | ~71 toques, ~64 teclas | **~72 toques, ~65 teclas** |

### Interrupção e retomada

| Situação | Antes | **Medido após 023** |
|---|---|---|
| Sessão expira no meio de uma parte e a pessoa envia | volta ao CPF sem aviso; marcações perdidas | **aviso claro** ([09](evidencias-reauditoria-023/09-sessao-expirada-aviso.jpg)); depois de digitar os dados, **volta direto à mesma parte com as marcações** ([10](evidencias-reauditoria-023/10-secao-recuperada.jpg)): 3 marcações e a idade restauradas, nada gravado antes do envio |
| Telas até voltar à parte depois da expiração | 3 (acesso, formações, parte vazia) | **2** (acesso, parte preenchida) |
| Recarregar no meio de uma parte | marcações perdidas | **marcações perdidas** (EF-02, mantido por decisão) |
| "Salvar e sair" e voltar | volta à parte certa, sem dizer onde parou | **"Você parou em «Informações do curso» · faltam no máximo 6 partes"** ([08](evidencias-reauditoria-023/08-declarante-onde-parou.jpg)) |
| Concluir uma formação com outra pendente | 4 toques e rolagem para achar a próxima | **1 toque** ([11](evidencias-reauditoria-023/11-proxima-formacao.jpg)) |

## 3. Situação dos achados da auditoria

| Achado | Grupo | Situação após 023 | Evidência |
|---|---|---|---|
| EF-01 sessão expirada sem aviso, com perda | B | **Resolvido** | Teste real de ponta a ponta (seção 2) |
| EF-02 a parte é a única unidade de salvamento | B/decisão | **Parcial:** "Salvar e sair" no meio das partes com mais de 8 perguntas; recarregar ainda perde | Recarregar a parte 2 de Diego zerou 4 marcações |
| EF-03 perguntas acadêmicas já conhecidas | C+D | **Aberto** (fora da 023) | Curso, campus, ano, modalidade e Q14 seguem perguntados |
| EF-04 declarante digita os dados duas vezes | D | **Aberto** | [07](evidencias-reauditoria-023/07-declarada-repeticao-s3.jpg) |
| EF-05 várias formações refazem tudo | D | **Aberto** | Diego refaria Q1–Q9 e a situação atual |
| EF-06 sem caminho para a próxima formação | A | **Resolvido** | [11](evidencias-reauditoria-023/11-proxima-formacao.jpg) |
| EF-07 sem noção de quanto falta | B | **Resolvido**, com nota (seção 4, R-03) | "Parte X · faltam no máximo N partes" em todas as partes |
| EF-08 complemento "Outro" gera erro | A | **Resolvido** | Cenário B sem reapresentação |
| EF-09 não confirmação sem critério | A | **Resolvido** | [04](evidencias-reauditoria-023/04-nao-confirmada-dois-passos.jpg) |
| EF-10 "Avaliação" longa e misturada | D | **Aberto** | Avaliação + Trabalha = 39% de toda a rolagem |
| EF-11 "(obrigatória)" em 50 perguntas | A | **Resolvido** | Só "(opcional)" visível |
| EF-12 Sim/Não empilhado | A | **Resolvido** | |
| EF-13 convite antes da 1ª pergunta | A | **Resolvido** | Primeira pergunta: 1,73 → 1,17 tela |
| EF-14 escala sem rótulo do 1 | D | **Aberto** | |
| EF-15 idade e ano em teclado alfabético | B/C | **Aberto** | |
| EF-16 Q6 e Q48 condicionais só no texto | D | **Aberto** | |
| EF-17 dica da data | A | **Resolvido** | [01](evidencias-reauditoria-023/01-acesso.jpg) |
| EF-18 selo vencido sem aviso | A | **Resolvido** (por teste) | |
| EF-19 retomada sem dizer onde parou | A | **Resolvido**; a reidentificação continua (decisão) | [08](evidencias-reauditoria-023/08-declarante-onde-parou.jpg) |
| EF-20 recusa dos termos parece conclusão | D | **Aberto** e mais visível (R-04) | |
| EF-21 dados estáveis entre Campanhas | D | **Aberto** | |
| EF-22 "Sair sem salvar" em toda parte | A | **Resolvido** | |
| EF-23 conclusão com ação abaixo | A | **Resolvido** | |
| EF-24 opções exclusivas | D | **Aberto** | |
| EF-25 declaração | A | **Resolvido** | [05](evidencias-reauditoria-023/05-declaracao-formulario.jpg), [06](evidencias-reauditoria-023/06-declaracao-confirmacao.jpg) |
| EF-26 confirmação com ação abaixo | A | **Resolvido** | [03](evidencias-reauditoria-023/03-concluida-acao-visivel.jpg) |

**Saldo:** dos 16 achados A e B, 15 estão resolvidos e 1 está parcial (EF-02, limitado por
decisão). Os 10 achados C e D continuam abertos, como planejado.

## 4. Achados novos

Todos são pequenos. Nenhum é regressão funcional.

| ID | Achado | Evidência | Grupo · prioridade |
|---|---|---|---|
| **R-01** | **"Seção" e "parte" convivem.** As partes dizem "Parte 4", "Parte anterior salva" e "volte a uma das partes", mas a entrada diz "Você responde uma **seção** de cada vez", o rodapé diz "Voltar à **seção** anterior" e os avisos de "Salvar e sair" dizem "O que você respondeu nesta **seção** está salvo". A pessoa tem de entender que são a mesma coisa | [02](evidencias-reauditoria-023/02-formacoes.jpg), [08](evidencias-reauditoria-023/08-declarante-onde-parou.jpg) | A · P2 |
| **R-02** | **O tamanho da pesquisa só aparece depois de começar.** A tela de formações promete "Ao final, você poderá ver sua trajetória", mas não diz quantas partes há. A mesma função do indicador daria "São no máximo 9 partes" antes do primeiro toque | [02](evidencias-reauditoria-023/02-formacoes.jpg) | A · P2 |
| **R-03** | **O "no máximo" erra para mais em 1 em quem não estuda.** No cenário A, a parte 1 diz "faltam no máximo 8", e vieram 7. A diferença se mantém até "Estudo" ("no máximo 2"; veio 1). É coerente com a regra (nunca subestimar) e com o texto ("no máximo"); não exige ação. Registrado para o teste com usuários verificar se a correção na última parte surpreende | Cenário A | Observação |
| **R-04** | **A recusa dos termos agora termina com mais aparência de sucesso.** Diego recusou (Q1 = "Não") e viu "Você chegou ao fim da pesquisa", depois "Suas respostas sobre Técnico em Química foram registradas. … Agradecemos a participação". Agora a tela também oferece a próxima formação. O comportamento é o mesmo; ficou mais visível. Continua dependendo da decisão sobre a recusa (EF-20, D) | Diego | D · P2 |
| **R-05** | **A lista do declarante tem hierarquia fraca.** O aviso de "Salvar e sair" aparece em texto comum, sem a caixa de aviso das outras telas, e "Continuar" é um link simples, enquanto nas formações a mesma ação é um botão primário | [08](evidencias-reauditoria-023/08-declarante-onde-parou.jpg) | A · P3 |

## 5. Teste de 30 segundos (revisado)

| Tela | Antes | Agora |
|---|---|---|
| Acesso | dica da data confundia | **passa** |
| Não confirmada | não passava (duas saídas sem critério) | **passa** |
| Formações (início) | passava, sem tamanho | **passa**, ainda sem tamanho (R-02) |
| Partes 1, 2, 8, 9, 11, 12, 13 | passavam, sem horizonte | **passam**, com horizonte |
| Informações do curso e Seção de curso | não passavam (perguntam o que a tela mostra) | **não passam** (EF-03, D) |
| Avaliação | passava com ressalvas (escala, complemento) | **passa**; resta a escala sem rótulo do 1 (EF-14, D) |
| Concluir e Concluída | passavam com ação abaixo | **passam** |
| Entrada após sessão expirada | não passava | **passa** |
| Declaração e confirmação | passavam parcialmente | **passam** |

Isso atende ao SC-011 da 023: todas as telas passam, exceto as que dependem da nova Versão.

## 6. Onde ainda está o esforço (cenário A)

| Fonte | Perguntas | Toques | Teclas | Rolagem | Natureza |
|---|---:|---:|---:|---:|---|
| Curso + Graduação (já sabidos: EF-03) | 6 | 11 | 4 | 3,5 telas (14%) | **estrutural, evitável** (C+D) |
| Avaliação + Trabalha (longas: EF-10) | 25 | 25 | 0 | 10,0 telas (39%) | estrutural, necessária; divisão possível (D) |
| Idade (derivável: EF-15) | 1 | 2 | 2 | — | **estrutural, evitável** (C) |
| Reidentificação a cada volta | — | 3 | 19 | — | decisão de garantia (018/DP-1808) |
| Demais perguntas | 14 | ~17 | — | ~8 telas | necessárias |

Para quem tem várias formações, cada formação extra custa de novo ~46 perguntas, das quais
~20 são sobre a pessoa e o presente (EF-05, D). É hoje o maior custo evitável por pessoa,
maior que o de EF-03.

## 7. Conclusão e recomendação

1. **A interface chegou perto do limite útil sem mudar o instrumento.** O que sobra no grupo
   A é pequeno: R-01, R-02 e R-05 cabem num ajuste de textos e de uma tela, de baixo custo.
   Recomendo fazê-lo junto com o próximo trabalho, não como feature à parte.
2. **O próximo salto é o pacote de decisões da CPAEG** para a Versão contextualizada:
   - DP-307: curso, campus, ano, modalidade e nível como contexto;
   - reaproveitamento entre formações (EF-05);
   - divisão da Avaliação (EF-10);
   - Q6, Q48, rótulo da escala, recusa e opções exclusivas.

   Pelos números acima, essas decisões tiram de 6 a 7 perguntas e 3,5 telas de todo egresso e
   ~20 perguntas por formação extra.
3. **O teste com egressos reais já faz sentido agora**, antes da nova Versão: a jornada está
   estável, sem perdas silenciosas nem erros evitáveis. O teste deveria medir:
   - tempo total;
   - hesitações em "Informações do curso", onde a reauditoria prevê atrito;
   - percepção do "no máximo N" (R-03);
   - reação à recusa dos termos (R-04).

   Esses dados também servem de evidência para a CPAEG. Como o sistema só roda com
   identidades fictícias, o teste é moderado: o egresso entra por uma persona e responde com a
   própria história.
4. **EF-02** (recarregar perde a parte) continua sendo a única fragilidade de perda de trabalho.
   A recomendação é decidir sobre a recuperação local **depois** do teste com usuários, como
   já combinado, usando a frequência observada de abas descartadas no celular.
