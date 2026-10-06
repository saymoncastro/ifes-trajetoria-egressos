# Auditoria de esforço de preenchimento da jornada do egresso

Data: 2026-10-05 · Base: `main` em `226ab6b` (após o PR #37, Feature 020)

Nada foi implementado: este documento só faz o diagnóstico. Não há spec, commit nem PR.

Esta é a quinta lente de UX do projeto. As anteriores trataram usabilidade
([008](2026-10-01-ux-feature-008.md)), identidade
([experiência](2026-10-02-identidade-da-experiencia.md),
[visual](2026-10-03-identidade-visual.md), [acesso](2026-10-03-identidade-acesso-egresso.md)),
celular ([mobile-first](2026-10-03-mobile-first-experiencia.md)) e convergência visual
([021](2026-10-04-021-convergencia-visual.md)). Esta auditoria não repete nenhuma delas. Ela
faz uma pergunta só: **quanto trabalho a jornada exige do egresso, e quanto desse trabalho o
sistema poderia fazer por ele?**

## Convenções

**Evidência.** **[obs]** observado executando a aplicação; **[cód]** lido no código;
**[est]** estimativa a partir de medidas observadas.

**Grupo de solução.** O pedido define três grupos. Esta auditoria precisa de um quarto,
porque vários itens não se encaixam em nenhum dos três: eles não dependem de dado acadêmico,
mas mudam o instrumento. Os quatro grupos nunca se misturam.

| Grupo | Significado |
|---|---|
| **A** | Só interface, fluxo ou comportamento, com dados e infraestrutura já existentes |
| **B** | Pequena alteração funcional (backend, consulta ou regra da jornada), sem mudar o instrumento |
| **C** | Depende de integração acadêmica real, que ainda não existe em produção |
| **D** | Depende de decisão metodológica ou de uma nova Versão do instrumento (CPAEG). Envolve uma `DECISÃO PENDENTE` já registrada |

**Tipo de esforço.** Cognitivo (entender, lembrar, decidir), motor (tocar, rolar, digitar),
informacional (fornecer o que já se sabe), corretivo (refazer, corrigir, recuperar).

**Prioridade.** **P0**: bloqueio ou risco grave de abandono. **P1**: fricção importante e
frequente. **P2**: melhoria relevante. **P3**: refinamento.

**Custo de implementação.** **PP**: horas, template ou CSS. **P**: até 2 dias, com teste.
**M**: uma feature pequena. **G**: depende de decisão institucional ou de integração.

---

## 1. Resumo executivo

**Para a egressa típica (Ana: uma formação, trabalha, não estuda), responder custa hoje 12
telas, 46 perguntas, cerca de 62 toques, 25 teclas e 27 telas de rolagem num celular de
375×812 [obs/est].** O custo maior não vem da interface. Ele vem de três fontes estruturais:

1. **O sistema pergunta o que ele mesmo mostra.** Na Seção "Informações do curso", logo
   abaixo do quadro "Você está respondendo sobre: Tecnologia em Análise e Desenvolvimento de
   Sistemas · Serra · 2022", vêm as perguntas "Em que ano você concluiu…", "Em qual campus…"
   (23 opções), "qual modalidade" e "Indique o questionário que pretende preencher". A Seção
   seguinte pede o curso numa lista de 50 opções. A tela de conclusão exibe Unidade, Data de
   conclusão, Nível e Modalidade. São 5 a 6 perguntas, 2 listas longas e o único campo de
   texto obrigatório do bloco, e tudo isso já é dado institucional
   ([evidência 05](evidencias-esforco/05-secao3-contexto-e-perguntas.jpg),
   [10](evidencias-esforco/10-concluir-contexto.jpg)). Remover essas perguntas depende da
   DP-307 e da nova Versão (grupos **C** e **D**), não de código.
2. **Há repetição em três escalas.** (a) O declarante informa curso, unidade, nível e ano e,
   um minuto depois, responde tudo de novo no instrumento
   ([evidência 17](evidencias-esforco/17-declarada-secao3.jpg)). (b) Quem tem duas ou três
   formações refaz o questionário inteiro para cada uma, inclusive cerca de 20 perguntas
   sobre a própria pessoa e sobre o presente: gênero, cor/raça, escolaridade dos pais,
   trabalho atual, salário, estudo atual. (c) Nas Campanhas seguintes, dados estáveis voltam
   a ser perguntados.
3. **Perder trabalho é fácil, e o sistema não explica quando isso acontece.** A sessão
   expira após 30 minutos sem uso. Se a pessoa toca em "Salvar e continuar" depois disso,
   volta à tela de CPF **sem nenhuma mensagem**, e o que marcou na Seção se perde
   ([evidência 12](evidencias-esforco/12-sessao-expirada-acesso.jpg), reproduzido com a
   inatividade reduzida a 1 minuto). Isso se soma ao achado MF-01 da auditoria mobile-first,
   ainda aberto: a Seção inteira é a única unidade de salvamento, e as Seções 8 e 9 têm
   5,3 telas cada.

**O que já funciona bem e deve ser preservado:** um toque para entrar na pesquisa; salvar
uma Seção incompleta é permitido e explicado; a pendência aparece sem cara de erro
("Ainda faltam estas perguntas… O que você respondeu nesta seção está salvo"); a retomada
leva à Seção certa; os condicionais da 006 são previsíveis; os valores enviados reaparecem
quando há erro; nenhum envio duplica dados.

**O que dá para resolver já, sem tocar no instrumento (A e B):** acabar com a perda
silenciosa por sessão expirada; criar um caminho da confirmação para a próxima formação
pendente; mostrar o complemento "Outro" só quando a opção estiver marcada (CSS `:has()`, sem
JavaScript), o que elimina o único erro de forma que recusa a Seção inteira; orientar a tela
"Não foi possível confirmar"; mostrar quanto falta; marcar as 4 perguntas opcionais em vez
das 50 obrigatórias; aproximar a primeira pergunta do topo. Isso quase não reduz perguntas
nem digitação. O ganho está no esforço corretivo e de orientação, que é o que mais provoca
abandono.

**A maior redução de esforço depende da DP-307 e da nova Versão (C e D).** Sem elas, o
número de perguntas não cai. Com elas, a egressa típica passa de 46 para 40 perguntas e de
2 campos de texto para nenhum no instrumento. O egresso com várias formações pode passar de
cerca de 46 para cerca de 26 perguntas a partir da segunda formação (seção 19).

**Recomendação:** sim, há fricção material. Ela justifica **uma feature de UX nos grupos A e
B**, sem tocar o instrumento, e **um pacote de decisões para a CPAEG**, que libere a Versão
contextualizada (seção 22).

---

## 2. Escopo analisado

**Percorrido na aplicação real** (modo demonstração, banco próprio `trajetoria_esforco`,
viewport 375×812 emulado no navegador do app):

| Cenário | Pessoa fictícia | O que foi exercitado |
|---|---|---|
| A — percurso simples | Ana Exemplo (TADS · Serra · 2022) | Acesso, entrada, as 8 Seções do percurso "trabalha / não estuda", pendência parcial na Seção 2, erro de complemento na Seção 8, revisão, conclusão, confirmação |
| B — condicionais | Fernanda (Técnico Subsequente) e leitura do instrumento | Ramos S5 (forma de oferta e 47 cursos), S10 ("Outro" com complemento), S12; percursos medidos no código |
| C — identificação e formação | Declarante fictício, Elisa (sem CPF), Bruno (duas formações) | "Não foi possível confirmar", formação declarada, repetição no instrumento, seleção entre formações, recusa dos termos (Q1 = Não) |
| Interrupção | Fernanda | Sessão expirada no meio de uma Seção, com o servidor reiniciado com `TRAJETORIA_SESSAO_INATIVIDADE=1`; retomada |

**Código inspecionado:** `interface/views.py`, `formularios.py`, `gravacao.py`,
`mensagens.py`, `apresentacao.py` e templates de Seção, pergunta, conclusão e aviso;
`acesso/` (formulário, sessão, normalização, template); `declaracao/` (views do egresso,
formulário, selo); `participacao/percurso.py` e `entrada.py`;
`formulario_2024/declaracao.py` (Q1 a Q54); `academico/models.py`;
`fonte_academica/cenarios.py`; `config/settings.py` (sessão e selo); o convite da 020.

**Documentos de referência:** Constituição (princípios III, XIII e XIV); spec 003 (Matriz
de Migração, DP-301 a DP-310); ADR 0003; spec 008 (FR-028, FR-080); spec 014 (fora de
escopo: autosave e JavaScript); spec 018 (DP-1808); auditoria mobile-first (MF-01).

**Fora do escopo:** estética, identidade visual e contraste, que já foram auditados. A Minha
Trajetória (021/022) e a página de e-mail (020) aparecem só como destino depois da
conclusão. A operação institucional (editor, acompanhamento, validação) não entra.

**Limites:** o navegador emulou um celular; não houve aparelho real nem medição de tempo
com pessoas. As contagens de toques e rolagem são estimativas fundamentadas: medidas de
altura de página observadas, mais a contagem de controles por pergunta. Não houve teste com
leitor de tela.

---

## 3. Jornada atual

```
/acesso/  CPF + data de nascimento ─┬─ confirmada ─▶ /formacoes/ ── "Iniciar" ─┐
                                    └─ não confirmada ─▶ [Conferir] | [Informar minha formação]
                                                                        │
                       /declaracao/ nome·unidade·nível·curso·ano ─▶ confirmação ─▶ "Começar"
                                                                        │
  ┌─────────────────────────────────────────────────────────────────────┘
  ▼
S1 Termos (Q1) ──Não──▶ /concluir/ ("Você chegou ao fim")
  │Sim
S2 Informações Pessoais (Q2–Q9, 8)
S3 Informações do curso (Q10–Q14, 5) ── Q14 escolhe o ramo ─▶ S4 | S5 | S6 | S7 (curso: 33/47/50/77 opções)
S8 Avaliação (Q20–Q33, 14) ── Q33 ─▶ S9 Trabalha (11) | S10 Não trabalha (1)
S11 Estudo (Q46–Q48, 3) ── Q46 ─▶ S12 Estuda (3) ─▶ S13 | S13
S13 sem título (Q52–Q54, 3)
  ▼
/concluir/ (contexto + lista de Seções + "Concluir pesquisa") ─▶ /concluida/ ─▶ Minha trajetória | e-mail
```

**Tamanho de cada tela no celular, cenário A [obs]** (altura total ÷ 812 px):

| Tela | Perguntas | Controles | Altura | Telas de rolagem | 1ª pergunta |
|---|---:|---|---:|---:|---:|
| Acesso | — | 2 textos | ~1 600 px (com o painel fictício) | — | — |
| Suas formações | — | 1 botão | 812 | 1,0 | — |
| S1 Termos e condições | 1 | 2 rádios | 1 970 | 2,4 | 1 405 px |
| S2 Informações Pessoais | 8 | 22 rádios, 1 texto, 2 listas (17), 1 caixa "sem resposta" | 2 753 | 3,4 | 397 px |
| S3 Informações do curso | 5 | 1 texto, 1 lista (23), 9 rádios | 1 961 | 2,4 | 397 px |
| S6 Graduação | 1 | 1 lista (50) | ~1 050 [est] | ~1,3 | 397 px |
| S8 Avaliação | 14 | 2 escalas (10 pontos), 20 rádios, 11 caixas, 2 textos | 4 296 | 5,3 | 397 px |
| S9 Egresso que trabalha | 11 | 52 rádios e pontos de escala, 2 caixas "sem resposta" | 4 300 | 5,3 | 397 px |
| S11 Estudo | 3 | 2 rádios, 8 caixas, 5 escalas, 1 caixa | 1 829 | 2,3 | 397 px |
| S13 (sem título) | 3 | 15 escalas | 1 687 | 2,1 | 397 px |
| Concluir a pesquisa | — | 8 links, 1 botão | 1 393 | 1,7 | — |
| Pesquisa concluída | — | 2 links | 1 123 | 1,4 | — |

Antes da primeira pergunta de cada Seção há sempre cerca de 400 px fixos: faixa de
demonstração, cabeçalho, título e "Você está respondendo sobre". Na S1, o convite de
abertura acrescenta mais 1 000 px.

---

## 4. Orçamento de interação atual

Contagem: rádio e escala = 1 toque; lista suspensa = 2 toques, mais a rolagem dentro dela;
caixa de seleção = 1 toque por item; texto = 1 toque para focar, as teclas e 1 toque para
fechar o teclado; cada envio = 1 toque. Rolagem = soma das alturas ÷ 812.

| Métrica | Cenário A (Ana) | Cenário B (Técnico Subsequente, não trabalha, estuda, usa "Outro") | Cenário C (não localizado, declara a formação) |
|---|---:|---:|---:|
| Telas (carregamentos) | 12 | 13 (+1 reapresentação por erro) | 15 |
| Seções | 8 | 9 | 8 |
| Perguntas apresentadas | 46 | 40 | 46 + 5 campos de declaração |
| Perguntas respondidas (obrigatórias) | 42 | 38 | 42 + 5 campos |
| Campos digitáveis obrigatórios | 4 (CPF, data, Q3, Q10) | 4 + 2 complementos | 7 (CPF, data, nome, curso, ano, Q3, Q10) |
| Teclas digitadas (aprox.) | 25 | 60 | 64 |
| Listas suspensas | 4 (17, 17, 23, 50 opções) | 4 (17, 17, 23, 47) | 6 (+ unidade e nível na declaração) |
| Toques (aprox.) | 62 | 66 | 71 |
| Rolagem (telas de 812 px) | ~27,6 | ~28 (inclui ~5 de volta ao erro) | ~29 |
| Decisões explícitas (respostas + escolhas de fluxo: iniciar, conferir/declarar, começar, concluir) | 44 | 40 | 50 |
| Perguntas cuja resposta a instituição já tem ou pode derivar | 6 (Q3, Q10, Q11, Q12, Q14, Q18) | 7 (Q3, Q10, Q11, Q12, Q14, Q16, Q17) | 6, e 4 delas já digitadas pela própria pessoa na declaração |
| Retornos e correções prováveis | 0–1 | 1 (erro do complemento) | 1–2 (conferir os dados e depois declarar) |

**Egresso com duas formações (Bruno) [cód/est]:** a segunda formação repete o cenário A
inteiro: +46 perguntas, +62 toques. Cerca de 20 dessas perguntas falam da pessoa ou do
presente, não da formação (seção 9.4).

**Retomada:** cada volta custa a reidentificação (2 campos, 19 dígitos, 3 toques) mais 1
toque em "Continuar a pesquisa" [obs].

---

## 5. Achados P0

### EF-01 — Sessão expirada no meio de uma Seção: o envio descarta as respostas e devolve à entrada sem explicação

- **Tela/fluxo:** qualquer Seção → envio → `/acesso/`.
- **Evidência [obs]:** Fernanda, Seção 2: marcou 6 respostas e digitou a idade, sem enviar.
  Esperou além do limite de inatividade (reduzido a 1 min só para o teste) e tocou em
  "Salvar e continuar". Resultado: tela "Confirme seus dados para acessar a pesquisa", sem
  aviso ([12](evidencias-esforco/12-sessao-expirada-acesso.jpg)). Ao entrar de novo, a
  Seção 2 aparece vazia.
  **[cód]** `TRAJETORIA_SESSAO_INATIVIDADE` = 30 min e `SESSION_EXPIRE_AT_BROWSER_CLOSE =
  True` (`config/settings.py:147-156`); `_pessoa` faz `redirect("/acesso/")` sem parâmetro
  (`interface/views.py:91-95`); a entrada não tem mensagem de sessão encerrada
  (`acesso/mensagens.py`).
- **Tipo:** corretivo e cognitivo. A pessoa não sabe o que aconteceu, se perdeu algo nem por
  que precisa digitar o CPF de novo.
- **Frequência provável:** baixa a média. Basta uma interrupção de 30 minutos no meio de uma
  Seção longa (S8 ou S9). No celular, isso é realista: ligação, trabalho, trânsito.
- **Impacto:** alto. Até 14 respostas perdidas, 19 dígitos para redigitar, nenhuma pista do
  motivo. É o tipo de evento que termina em abandono.
- **Proposta:**
  1. (B, PP) Distinguir "sessão expirada" de "sem sessão". Redirecionar para
     `/acesso/?aviso=sessao`, com o texto: "Por segurança, sua sessão foi encerrada depois de
     um tempo sem uso. O que você já tinha salvo continua guardado. Confirme seus dados para
     continuar."
  2. (B, P) Depois da nova confirmação, voltar direto à Seção onde a pessoa estava, por um
     destino interno validado (só `/participacoes/<uuid>/…` da própria Pessoa), em vez de
     `/formacoes/`.
  3. (B, M) Preservar o envio: quando o POST de uma Seção chega com a sessão expirada,
     apresentar a reidentificação na própria resposta, levando os campos enviados (tudo no
     servidor, sem JavaScript). Confirmada a identidade da mesma Pessoa, aplicar a gravação.
  4. (D) Avaliar se 30 minutos é adequado para uma pesquisa de cerca de 15 minutos com
     interrupções. O parâmetro já existe; a decisão é de segurança e de garantia (018).
- **Custo:** PP (1), P (2), M (3).
- **Dependências:** 3 exige revisão de segurança (a confirmação precisa resolver a mesma
  Pessoa dona da Participação; CSRF continua valendo).
- **Risco semântico:** nenhum. A gravação continua sendo a da 005.

### EF-02 — A Seção é a única unidade de salvamento, e há Seções de 5 telas (MF-01 continua aberto)

- **Tela/fluxo:** S2, S8 e S9.
- **Evidência:** MF-01 da [auditoria mobile-first](2026-10-03-mobile-first-experiencia.md#mf-01--interromper-no-meio-de-uma-seção-descarta-tudo-o-que-foi-marcado-o-salvamento-parcial-existe-mas-está-escondido-e-aparece-como-erro)
  [obs na época]. O polish da 014 corrigiu a comunicação: hoje a tela de entrada diz que se
  pode salvar a Seção incompleta, e a pendência aparece sem cara de erro [obs]. O mecanismo
  não mudou: recarregar a página ou ter a aba descartada pelo sistema apaga tudo o que foi
  marcado e não enviado. A 014 excluiu de propósito autosave, armazenamento local e
  JavaScript.
- **Tipo:** corretivo.
- **Frequência:** depende de quanto o celular descarta abas em segundo plano. Não foi
  medido em aparelho (como já dizia a MF-01).
- **Impacto:** alto nas S8 e S9 (14 e 11 perguntas, 5,3 telas cada).
- **Proposta:**
  - (A, PP) Lembrete no meio das Seções longas, sem mecanismo novo: um segundo bloco
    "Salvar e continuar depois" na metade das Seções com mais de 8 perguntas. É o mesmo
    botão "Salvar e sair", que já existe e já salva incompletas. Divide o risco de perda pela
    metade sem mexer no instrumento.
  - (B/decisão) Reavaliar a exclusão da 014: uma melhoria progressiva que guarde no
    `sessionStorage` só as marcações não enviadas da Seção aberta e as restaure ao recarregar.
    Sem JavaScript, nada muda (o FR-080 da 008 continua cumprido). A decisão é do
    solicitante, porque contraria uma exclusão explícita da 014.
  - (D) Seções menores numa nova Versão (ver EF-10).
- **Custo:** PP (lembrete); P (melhoria progressiva).
- **Risco semântico:** nenhum.

---

## 6. Achados P1

### EF-03 — O instrumento pergunta o que a instituição já sabe e o que a própria tela exibe

- **Tela/fluxo:** S3 e S4 a S7.
- **Evidência [obs]:** na S3, abaixo de "Você está respondendo sobre: Tecnologia em Análise
  e Desenvolvimento de Sistemas · Serra · 2022", vêm Q10 "Em que ano você concluiu o seu
  curso no Ifes?" (texto, com "Exemplo: 2020, 2021, 2022, etc."), Q11 "Em qual campus…"
  (lista de 23), Q12 "qual modalidade" e Q14 "Indique o questionário que pretende
  preencher" ([05](evidencias-esforco/05-secao3-contexto-e-perguntas.jpg)). A S6 pede o
  curso numa lista de 50 ([06](evidencias-esforco/06-secao6-curso.jpg)). A tela "Concluir"
  mostra Curso, Unidade, Data de conclusão (16/12/2022), Nível e Modalidade
  ([10](evidencias-esforco/10-concluir-contexto.jpg)).
  **[cód]** `formulario_2024/declaracao.py:442-502`; `ConclusaoAcademica` tem curso,
  unidade, nível, modalidade, forma de oferta, ano e data (`academico/models.py`); o FR-028
  da 008 proíbe pré-preencher, sugerir, ocultar ou pular Q10–Q19; o ADR 0003 mantém Q14
  declarada.
- **Tipo:** informacional, cognitivo ("o sistema não sabe quem eu sou?"; "questionário que
  pretende preencher" expõe a estrutura interna) e motor (2 listas longas, 1 campo de texto).
- **Frequência:** 100% das Participações ancoradas em Conclusão.
- **Impacto:** é o maior desperdício isolado da jornada. São 5 a 6 perguntas e 1 Seção
  inteira, e a coerência visível da pesquisa sofre. Há ainda o risco de dado divergente já
  documentado (ADR 0003: nível Técnico respondendo o ramo Pós-Graduação).
- **Proposta (C + D):** retirar Q10, Q11, Q12, Q14, Q15–Q19 e Q16 da jornada quando houver
  Conclusão, decidir a navegação dos ramos S4–S7 pelo nível institucional e manter o quadro
  "Você está respondendo sobre" como a única apresentação dessas informações. É exatamente
  o que a Constituição XIV prescreve ("contextualizar em vez de perguntar") e o que a DP-307
  deixou pendente. A memória de produto de 2026-10-03 já registra a direção: curso, unidade,
  ano e nível são contexto da formação, fora da nova Versão.
- **Não é possível agora:** sem a DP-307, sem correspondência entre o vocabulário da fonte e
  as Opções (001/DP-007) e sem fonte real (001/DP-001, DP-004), qualquer pré-preenchimento
  gravaria dado institucional como declarado, o que viola o princípio III. **Não recomendo
  paliativo de interface aqui.**
- **Custo:** G (decisão e nova Versão). A engenharia é M depois da decisão.
- **Risco semântico:** **alto, e por isso exige discussão.** Muda o significado do dado
  (de declarado para institucional) e a comparabilidade com 2024.

### EF-04 — Quem declara a formação digita os mesmos dados duas vezes, com um minuto de intervalo

- **Tela/fluxo:** `/declaracao/` → S3 e S4 a S7.
- **Evidência [obs]:** o declarante preencheu "Seu nome", "Unidade do Ifes" (lista de 7),
  "Nível de ensino" (lista de 3), "Curso" (texto livre) e "Ano de conclusão"
  ([15](evidencias-esforco/15-declaracao-formulario.jpg)), confirmou e, na S3, recebeu de
  novo ano, campus (agora lista de 23, com outro vocabulário), modalidade e Q14 ("Técnico"
  versus "Técnico Concomitante/Subsequente/EJA-PROEJA"), e depois o curso numa lista
  ([17](evidencias-esforco/17-declarada-secao3.jpg)).
- **Tipo:** informacional e cognitivo (vocabulários diferentes para a mesma coisa).
- **Frequência:** 100% do caminho declarado (cenário C).
- **Impacto:** alto nesse público, que já é o de maior atrito (não foi encontrado e precisou
  se explicar).
- **Classificação da repetição:** **claramente eliminável.** As duas informações são
  declaradas pela mesma pessoa, na mesma sessão.
- **Proposta (D, depois B):** com a nova Versão sem Q10–Q19 (EF-03), a repetição some sem
  custo extra, porque a FormacaoDeclarada passa a ser o contexto. Enquanto a baseline
  vigorar, o pré-preenchimento de Q10/Q11/Q14 a partir da FormacaoDeclarada depende da mesma
  correspondência de vocabulário da DP-307. Não recomendo implementar antes.
- **Custo:** zero com a nova Versão; P com a baseline (depois da decisão).
- **Risco semântico:** médio (correspondência de vocabulário).

### EF-05 — O egresso com várias formações refaz o questionário inteiro, inclusive o que é sobre ele, não sobre a formação

- **Tela/fluxo:** `/formacoes/` (seleção) → Participação 1 → … → Participação 2.
- **Evidência [obs/cód]:** a tela de Bruno diz "Cada formação tem sua própria pesquisa"
  ([18](evidencias-esforco/18-selecao-bruno.jpg)). Cada Participação percorre S1 a S13 desde
  o início. Perguntas que não dependem da formação, só da pessoa ou do presente:
  Q1 (termo), Q2 a Q9 (8: gênero, idade, cor/raça, PcD, estado civil, escolaridade dos
  pais), Q33 (trabalha?), Q34, Q35, Q37, Q38, Q39 e Q40 (setor, exigência do cargo, chefia,
  remuneração, porte, localização), Q45, Q46, Q49 e Q51. São de 18 a 22, conforme o
  percurso.
- **Tipo:** informacional e motor.
- **Frequência:** todos os egressos com mais de uma Conclusão. A verticalização (técnico,
  depois graduação, depois pós) é comum no Ifes. O cenário de demonstração tem 3 pessoas
  nesse caso.
- **Impacto:** a segunda formação custa +46 perguntas, das quais cerca de 20 já foram
  respondidas minutos antes. A terceira, mais 46.
- **Classificação:** **potencialmente eliminável.** Exige decisão, porque cada Participação
  é independente (princípio I) e as respostas pertencem à Participação e à Versão.
- **Proposta (D, depois B):** dentro da mesma Campanha e da mesma Versão, oferecer as
  respostas da Participação irmã já concluída como valores iniciais **visíveis e editáveis**
  das perguntas sobre a pessoa e o presente, com a frase "Trouxemos o que você respondeu
  sobre {outra formação}. Confira e altere se precisar." A Resposta continua declarada e
  gravada na Participação nova. Nada é copiado sem envio.
- **Alternativa sem mexer na semântica (A, PP):** avisar na tela de seleção quanto custa
  ("Cada formação tem sua própria pesquisa, com perguntas sobre aquele curso.") e começar
  pela formação mais recente. Isso é decisão de produto, porque a 014 FR-035 manda não
  reordenar.
- **Custo:** M, depois da decisão.
- **Risco semântico:** **médio.** Valor inicial induz a confirmar sem ler (ancoragem). Exige
  regra sobre quais perguntas são "da pessoa" (marcação na Versão). Decisão da CPAEG.

### EF-06 — Depois de concluir uma formação, não há caminho para a próxima formação pendente

- **Tela/fluxo:** `/concluida/`.
- **Evidência [cód]:** `concluida.html:11-12` oferece só "Ver minha trajetória no Ifes" e o
  convite de e-mail. A volta para `/formacoes/` fica no fim da página da Minha trajetória
  (`narrativa/minha_trajetoria.html:92`). Para Bruno, a segunda formação exige: abrir a
  Minha trajetória, rolar até o fim, "Voltar às suas formações", escolher, iniciar.
- **Tipo:** cognitivo (descobrir o próximo passo) e motor.
- **Frequência:** todos os egressos com mais de uma formação pendente.
- **Impacto:** risco real de a pessoa achar que terminou e nunca responder a segunda.
- **Proposta (A, PP):** quando a Pessoa tem outra formação pendente, mostrar na confirmação,
  acima da Minha trajetória: "Você também pode responder sobre {curso · unidade · ano}" com
  o botão "Responder sobre esta formação". A consulta `situacao_de_entrada` já existe.
- **Risco semântico:** nenhum.

### EF-07 — A pessoa não sabe quanto falta, e os títulos expõem a estrutura interna

- **Tela/fluxo:** todas as Seções; "Concluir".
- **Evidência [obs]:** não há indicação de progresso. O título da aba da última Seção é
  "Seção 13" (para quem passou por 8 Seções), e a revisão lista "Seção 13". "Egresso que
  trabalha" e "Egresso que estuda" descrevem a regra do instrumento, não o assunto. A
  primeira tela não diz a duração nem a quantidade de partes.
- **Tipo:** cognitivo ("onde estou?", "quanto falta?").
- **Frequência:** 100%.
- **Impacto:** sem horizonte, as Seções de 5 telas parecem não ter fim. É uma causa
  conhecida de abandono no meio.
- **Proposta:**
  - (B, P) Indicador honesto, calculado no servidor a partir da Versão e do percurso da 006:
    "Parte 4 · faltam no máximo 4". O "no máximo" vem do caminho mais longo pelas regras
    restantes, uma função pura sobre `ConteudoVersao`. Não é percentual, para não mentir
    quando um ramo encurta o caminho.
  - (A, PP) Título da aba de Seção sem título igual ao `h1` (título da pesquisa), em vez de
    "Seção {posição}". Na revisão, a mesma regra.
  - (D) Títulos de Seção voltados ao assunto ("Seu trabalho atual", "Seus estudos") numa
    nova Versão.
- **Custo:** P (indicador), PP (título).
- **Risco semântico:** nenhum.
- **Nota:** a auditoria mobile-first deixou progresso fora de escopo. Esta auditoria
  recomenda incluí-lo, mas só na forma de contagem honesta de partes.

### EF-08 — O complemento "Outro" fica sempre visível, e preenchê-lo sem marcar a opção recusa a Seção inteira

- **Tela/fluxo:** S8 (Q26 e Q32), S10 (Q45).
- **Evidência [obs]:** na S8, digitar "Pôster" em "Descreva: «Outro»" sem marcar "Outro:"
  fez a Seção inteira voltar com "Há problemas nesta seção". Nada das 14 respostas foi
  gravado (envio atômico), e o resumo apontava para uma pergunta 3 telas abaixo
  ([09](evidencias-esforco/09-secao8-erro-complemento.jpg)). **[cód]**
  `formularios.py:clean` recusa, por regra da 005 (FR-030 a).
- **Tipo:** corretivo e cognitivo. O campo de descrição aparece pronto para receber texto,
  e o natural é digitar direto.
- **Frequência:** média. São 3 perguntas com complemento, e Q26/Q32 estão no percurso de
  todos.
- **Impacto:** o único erro de forma da jornada, e cai justamente na Seção mais longa.
- **Proposta (A, PP):** colocar o campo de descrição dentro da Opção que o admite e
  mostrá-lo só quando ela estiver marcada, com CSS (`.pergunta:has(.opcao-com-complemento
  input:checked) .complemento`). Sem `:has()`, o campo continua visível como hoje. Rótulo:
  "Descreva o que se encaixa em «Outro»".
- **Complemento (B, decisão):** se a pessoa desmarca "Outro" depois de digitar, o texto
  oculto continua sendo enviado e gera o mesmo erro. Ignorar o complemento quando a Opção
  não está marcada muda a 005 FR-030 (texto descartado). Decidir explicitamente.
- **Não recomendado:** marcar "Outro" automaticamente porque há texto. Isso infere uma
  resposta declarada (princípio III).
- **Risco semântico:** nenhum para a proposta A.

### EF-09 — "Não foi possível confirmar" oferece duas saídas e nenhum critério para escolher

- **Tela/fluxo:** `/acesso/` após uma falha.
- **Evidência [obs]:** aparecem o aviso "Não foi possível confirmar os dados informados.
  Confira os dados abaixo e tente novamente. Conferir os dados", o botão "Informar minha
  formação" (sem explicação) e, no topo, "Continuar para suas formações", que sobra da sessão
  de outra pessoa que usou o mesmo navegador
  ([14](evidencias-esforco/14-nao-confirmada.jpg)).
- **Tipo:** cognitivo (decisão sem informação).
- **Frequência:** todos os não localizados. É o público do cenário C, que inclui egressos
  antigos e pessoas sem CPF na fonte (Elisa).
- **Impacto:** escolher errado custa caro. Declarar quando era só um dígito errado gera uma
  validação institucional desnecessária. Insistir quando a pessoa não está na base leva ao
  limite de tentativas.
- **Proposta (A, PP):** um bloco só, em ordem: "1. Confira se o CPF e a data estão certos.
  [Conferir os dados]. 2. Se estão certos, pode ser que sua formação ainda não esteja na
  nossa base. [Informar minha formação], e ela passará por verificação." Esconder "Continuar
  para suas formações" quando a tentativa atual falhou. Na demonstração isso é um artefato
  do painel, mas em produção vale para computadores compartilhados.
- **Risco semântico:** nenhum.

### EF-10 — A Seção "Avaliação" mistura experiências do curso com a situação atual, e a pergunta que decide o ramo fica no fim de 5 telas

- **Tela/fluxo:** S8.
- **Evidência [obs]:** 14 perguntas, 4 296 px. De Q20 a Q32: cultura, extensão, monitoria,
  estágio, publicações, bolsa (durante o curso). Q33, "Atualmente você trabalha?", decide
  S9/S10 e é a última ([07](evidencias-esforco/07-secao8-topo.jpg)).
- **Tipo:** cognitivo (troca de contexto: do passado ao presente) e motor (rolagem).
- **Frequência:** 100%.
- **Impacto:** a Seção mais longa, a que mais expõe a perda descrita em EF-01 e EF-02, e a
  mudança de assunto acontece na própria pergunta de ramificação.
- **Proposta (D):** numa nova Versão, dividir S8 em "Durante o curso" (Q20–Q32) e abrir o
  bloco de trabalho com Q33. A ordem das perguntas não muda; só a fronteira de Seção. Até
  lá: (A) as mitigações de EF-02 e EF-12.
- **Risco semântico:** baixo (mesmas perguntas, mesma ordem), mas exige nova Versão (VIII).

---

## 7. Achados P2

| ID | Tela | Problema e evidência | Tipo | Proposta | Grupo · custo | Risco semântico |
|---|---|---|---|---|---|---|
| **EF-11** | Todas as Seções | "(obrigatória)" em 50 das 54 perguntas, às vezes numa linha só para isso [obs; `_enunciado.html`]. Ruído de leitura e cerca de 1 tela de rolagem a mais no cenário A | cognitivo, motor | Marcar só as 4 opcionais ("(opcional)": Q6, Q42, Q44, Q48) e dizer uma vez, no topo da primeira Seção: "Todas as perguntas são obrigatórias, exceto as marcadas como opcionais." Manter `aria-required` | A · PP | nenhum |
| **EF-12** | S1, S2, S8, S9, S11 | 14 perguntas Sim/Não no percurso A, cada uma com duas linhas de rádio empilhadas [obs] | motor | Sim/Não lado a lado (duas células, como a escala), mantendo alvo ≥ 44 px e a ordem de leitura. Só CSS para perguntas de 2 Opções curtas | A · PP | nenhum |
| **EF-13** | S1 | O convite de abertura (4 parágrafos) é reapresentado depois que a pessoa já tocou em "Iniciar". A única pergunta fica a 1 405 px [obs; [03](evidencias-esforco/03-secao1-topo.jpg), [04](evidencias-esforco/04-secao1-pergunta.jpg)] | cognitivo, motor | Recolher o convite num `<details>` "Sobre esta pesquisa" (o texto da Versão é preservado), mantendo o termo visível por inteiro (princípio XVII) | A · PP | nenhum (o texto continua apresentado) |
| **EF-14** | S8, S9, S11, S13 | A escala mostra só "5 = Concordo totalmente"; o ponto 1 não tem rótulo (DP-301). O prefixo "Indique o seu grau de concordância com a afirmação" se repete 10 vezes [obs] | cognitivo | Decidir a DP-301. Na nova Versão, agrupar as afirmações sob um enunciado único por bloco | D · G | baixo |
| **EF-15** | S2, S3 | Q3 (idade) e Q10 (ano) são texto livre, sem `inputmode` numérico: abre o teclado alfabético [obs: `type=text`, sem `inputmode`]. Aceita "vinte e cinco" | motor | (B) atributo de formato na Pergunta da Versão ("número inteiro") que a interface traduz em `inputmode="numeric"`, sem tratamento por pergunta. (C) Q3 derivada da data de nascimento da fonte; Q10 sai com EF-03 | B · P / C | baixo (B); alto (C, princípio III) |
| **EF-16** | S2, S11 | Q6 ("Se sim, qual a deficiência?") aparece para todos, com a caixa "Deixar esta pergunta sem resposta" (DP-303). Q48 diz em texto "Caso não tenha estudado mais deixe essa resposta em branco" (DP-302) [obs] | cognitivo | Decidir DP-303 e DP-302. Uma vez decididas, a exibição condicional pode ser feita com CSS `:has()`, sem JavaScript e sem nova capacidade de navegação | D · G (decisão), PP (execução) | **médio:** muda quem vê a pergunta |
| **EF-17** | Acesso | A dica "DD/MM/AAAA" convive com `inputmode="numeric"`, cujo teclado no iOS não tem "/". O sistema aceita 8 dígitos, mas não diz isso. Nenhum campo recebe foco inicial [obs: login com `12041998` funcionou; [01](evidencias-esforco/01-acesso.jpg)] | cognitivo, motor | Dica: "Só os números, como 12041998". Na mesma linha, CPF: "Só os números". Não usar `autofocus` (acessibilidade); o ganho está na dica | A · PP | nenhum |
| **EF-18** | Declaração | O selo do declarante vale 30 min. Vencido, "Continuar" ou "Começar" levam de volta a `/acesso/` sem aviso, e o formulário preenchido se perde [cód: `views_egresso.py:87-88, 117`; `settings.py:174`] | corretivo | Aviso na entrada ("Por segurança, confirme seus dados de novo. Nada foi registrado ainda.") e manter os campos da declaração na nova tentativa | A/B · PP | nenhum |
| **EF-19** | Retomada | Cada retorno exige CPF e data (19 dígitos), e o convite por e-mail da 020 leva à tela de entrada genérica [obs; `convite_real.html:9`]. Depois, "Continuar a pesquisa" e não a Seção diretamente [obs; [13](evidencias-esforco/13-retomada.jpg)] | motor, informacional | (A, PP) Na tela de formações, dizer onde a pessoa parou: "Você parou em Avaliação. Faltam no máximo 3 partes." (D) Mecanismo de retorno de menor fricção (link de continuação) é DP-1808 / 004 DP-406, decisão de garantia | A · PP / D · G | nenhum |
| **EF-20** | S1 → Concluir | Q1 = "Não" leva a "Concluir a pesquisa: Você chegou ao fim da pesquisa…", com a lista "Termos e condições" e o botão "Concluir pesquisa". A recusa só é registrada com esse segundo toque, e o texto não diz que recusar encerra a participação [obs] | cognitivo | (D) A forma de tratar a recusa (O-17 da 003; 002/DP-007) é decisão do instrumento. A interface não pode tratar Q1 de forma especial (FR-034). Sugestão para a decisão: explicar a consequência junto à pergunta | D · G | médio |
| **EF-21** | Campanhas seguintes | Dados estáveis (Q2, Q4, Q8, Q9; Q5) serão perguntados de novo a cada Campanha [cód: nenhuma leitura de Participação anterior] | informacional | Mesma solução de EF-05, aplicada entre Campanhas: valor inicial editável vindo da Participação anterior da mesma Pessoa. Só com decisão explícita, porque toca o princípio I (longitudinalidade) e a ancoragem | D · M | **alto** |

---

## 8. Achados P3

| ID | Tela | Problema | Proposta | Grupo · custo |
|---|---|---|---|---|
| **EF-22** | Rodapé de cada Seção | Dois botões e até dois links com notas ("Voltar à seção anterior: alterações não salvas serão descartadas"; "Sair sem salvar esta seção: o que já foi salvo continua guardado"). "Sair sem salvar" serve só a quem quer descartar o que marcou, um caso raro, e já existe "Salvar e sair" [obs; `secao.html:36-37`] | Retirar "Sair sem salvar esta seção" ou reduzi-lo a "Sair" no cabeçalho. Teste do "por que estou fazendo isso": perde-se só a possibilidade de descartar, que o egresso pode obter não salvando | A · PP |
| **EF-23** | Concluir a pesquisa | O aviso "depois de concluída, ela não poderá ser alterada" e a ação ficam abaixo de um bloco de 6 linhas de contexto (1,7 tela). A revisão é só uma lista de nomes de Seção, com "Seção 13" [obs] | Ordem: frase de fim, aviso de irreversibilidade, botão "Concluir pesquisa", e só depois "Revisar uma seção" e o contexto | A · PP |
| **EF-24** | S8, S11 | Opções exclusivas não são modeladas: "Artigos" + "Não houve" foi aceito; o mesmo vale para "Não recebi" (Q32) e "Não estudei mais" (Q47) [obs; [08](evidencias-esforco/08-secao8-nao-houve-e-artigos.jpg)] | Capacidade "Opção exclusiva" na Versão (validação de forma, como o complemento), decidida com a CPAEG. Afeta mais a qualidade do dado que o esforço | D · M |
| **EF-25** | Declaração | "Seu nome" sem `autocomplete="name"`; nível em lista de 3 (rádios são 1 toque); a confirmação não mostra o nível e não tem "Corrigir"; "Começar" e "Sair" têm o mesmo peso visual [obs; [16](evidencias-esforco/16-declaracao-confirmacao.jpg)] | `autocomplete="name"`; nível em rádios; confirmação com a linha completa (com nível) e o link "Corrigir"; "Começar" como ação primária | A · PP |
| **EF-26** | Pesquisa concluída | A ação principal ("Ver minha trajetória no Ifes", prometida desde a tela de entrada) fica abaixo da dobra, depois do contexto completo e do encerramento da Versão [obs; [11](evidencias-esforco/11-concluida.jpg)] | Ação logo depois da confirmação; contexto depois | A · PP |

---

## 9. Análise por dimensão de esforço

### 9.1 Esforço cognitivo

| Onde | O que a pessoa precisa entender ou decidir | Tratamento |
|---|---|---|
| Q14 "Indique o questionário que pretende preencher" | Que existe mais de um "questionário" e qual é o dela, relacionando a palavra ao nível do curso | EF-03 (D/C) |
| Contexto × perguntas na S3 | Por que perguntam o que está escrito logo acima; se deve responder igual ou "corrigir" | EF-03 |
| "Não foi possível confirmar" | Se errou o dado ou se não está na base | EF-09 (A) |
| Escalas sem rótulo do ponto 1 | O que 1 significa | EF-14 (D) |
| Complemento "Outro" | Que precisa marcar antes de descrever | EF-08 (A) |
| Q6 e Q48 | Se deve responder (condição só no texto) | EF-16 (D) |
| Títulos "Egresso que trabalha", "Seção 13" | Linguagem de regra interna | EF-07 (A/D) |
| Q1 = Não | Que recusar encerra a participação | EF-20 (D) |
| Seleção entre formações | Que fará a pesquisa N vezes | EF-05 |

**O que está bom:** mensagens de pendência ("Ainda faltam estas perguntas") com âncoras;
"Você está respondendo sobre" em todas as Seções; texto de entrada que explica a dinâmica
("Você responde uma seção de cada vez. Pode salvar a qualquer momento…").

### 9.2 Esforço de digitação

Ver o mapa completo na seção 12. Resumo: no cenário A, só 4 campos são de digitação
obrigatória, e 2 deles (Q3 e Q10) são dados que a instituição tem ou pode derivar. A
digitação é pequena. O problema é ela ser **desnecessária**, e Q3/Q10 abrirem o teclado
alfabético.

### 9.3 Número de interações

O volume é dominado por perguntas de 1 toque (rádio e escala). Há poucas interações sem
valor informacional; as principais estão na seção 13. As listas suspensas custam 2 toques
mais a rolagem interna: Q8/Q9 (17 opções) são inevitáveis; Q11 (23) e o curso (33 a 77)
são eliminações de EF-03.

### 9.4 Repetição

| Informação | Onde se repete | Classificação |
|---|---|---|
| Ano, unidade, nível, curso (formação conhecida) | Quadro de contexto, S3/S4–S7, tela de conclusão | **Claramente eliminável** (EF-03; depende de C/D) |
| Ano, unidade, nível, curso (formação declarada) | Formulário de declaração, depois S3/S4–S7 | **Claramente eliminável** (EF-04; D) |
| Data de nascimento → idade (Q3) | Digitada no acesso; idade pedida 2 telas depois | **Potencialmente eliminável** (C: a data não é guardada em claro; derivar exige a fonte; princípio III exige que seja derivada, nunca declarada) |
| Q1, Q2–Q9, situação de trabalho e estudo | Uma vez por formação | **Potencialmente eliminável** (EF-05; D) |
| Q2, Q4, Q8, Q9 | Uma vez por Campanha | **Potencialmente eliminável** (EF-21; D, risco alto) |
| CPF e data | A cada retomada | **Necessária** hoje (garantia da 018); reduzível por decisão (EF-19) |
| "Você está respondendo sobre" | Em toda Seção | **Necessária**: é orientação, não pergunta; custa cerca de 90 px |

### 9.5 Pré-preenchimento e defaults

Ver a seção 11. Nenhum default seguro de opção foi encontrado no instrumento atual. Todas
as perguntas declaradas têm respostas plausíveis em várias Opções, e marcar uma por padrão
induziria resposta. **Não recomendo nenhum default de resposta.** Os ganhos possíveis são
contexto institucional (EF-03) e reaproveitamento de respostas da própria pessoa, visível e
editável (EF-05 e EF-21, com decisão).

### 9.6 Divulgação progressiva

Ver a seção 14. Os ramos por Seção (Q1, Q14, Q33, Q46) já funcionam como divulgação
progressiva, e bem. As lacunas são dentro da Seção: Q6, Q48 e os complementos.

### 9.7 Ordem das perguntas

- Começa por um termo de 2,4 telas (S1) e por dados sensíveis (S2: gênero, cor/raça,
  deficiência), antes de qualquer pergunta sobre a formação. A ordem é herdada e deve ser
  preservada na baseline (XIII). Para a nova Versão, a CPAEG pode considerar começar pelo
  que a pessoa reconhece com facilidade (trabalho e estudos atuais) e deixar os dados
  sensíveis para o fim (D).
- A S8 mistura passado e presente e põe a ramificação no fim (EF-10).
- Q47/Q48 ("Após o curso, você…") vêm depois de Q46 ("Atualmente você estuda?"), que já
  decidiu o ramo. A ordem é a original (DP-302).

### 9.8 Escolha dos componentes

| Tipo | Componente atual | Avaliação |
|---|---|---|
| Escolha única ≤ 10 Opções | Rádios empilhados | Adequado. Sim/Não poderia ser lado a lado (EF-12) |
| Escolha única > 10 Opções | Lista suspensa (`LIMITE_RADIOS = 10`) | Adequado para Q8/Q9 (17, ordinais). Para cursos (33 a 77), a lista é ruim no celular, mas a solução é eliminar (EF-03), não trocar o componente. Busca/autocomplete só se a pergunta sobreviver na nova Versão, e mesmo assim depois de medir |
| Escala 1–5 | Cinco células tocáveis | Adequado; falta o rótulo do ponto 1 (EF-14) |
| Escolha múltipla | Caixas | Adequado; faltam opções exclusivas (EF-24) |
| Texto curto | `input type=text` | Inadequado para Q3 e Q10 (números) (EF-15) |
| "Deixar sem resposta" | Caixa extra em 4 rádios e escalas opcionais | Necessária sem JavaScript (rádio não se desmarca); custo baixo |
| Nível na declaração | Lista de 3 | Rádios seriam 1 toque e mostrariam tudo (EF-25) |

### 9.9 Erros e validação

Ver a seção 15. Ponto central: a única validação de forma que recusa o envio (complemento
sem Opção) é **evitável na interface** (EF-08). As pendências são bem tratadas.

### 9.10 Interrupção e retomada

Ver a seção 16. Dois buracos: a sessão expirada é silenciosa e perde dados (EF-01), e o
recarregamento perde a Seção (EF-02).

### 9.11 Sensação de progresso

| Pergunta | Resposta hoje | Proposta |
|---|---|---|
| Onde estou? | Título da Seção (alguns internos) e "Você está respondendo sobre" | Títulos legíveis (EF-07) |
| Quanto falta? | **Não há como saber** | "Parte X · faltam no máximo N" (EF-07) |
| Meu trabalho foi salvo? | Só depois de "Salvar e continuar" com pendência, ou de "Salvar e sair". Ao avançar sem pendência, nada confirma que foi salvo | Uma frase discreta na Seção seguinte: "Parte anterior salva." (A, PP) |
| Posso continuar depois? | Sim, dito na entrada | Repetir junto aos botões das Seções longas (EF-02) |
| O que acontece ao concluir? | "Depois de concluída, ela não poderá ser alterada"; a Minha trajetória é antecipada na entrada | Bom; reordenar (EF-23) |

### 9.12 Densidade e ritmo

Ritmo irregular: 1 pergunta (S1, S6), 3 (S11, S13), 5 (S3), 8 (S2), 11 (S9), 14 (S8). As
duas Seções mais longas somam 25 das 46 perguntas e 10,6 das 24,5 telas de rolagem das
Seções. Não se recomenda uma pergunta por tela nem fundir Seções. O desequilíbrio é do
instrumento (EF-10, D). Na interface, EF-11, EF-12 e EF-13 tiram cerca de 3 telas de
rolagem.

### 9.13 Escolhas binárias

14 Sim/Não no percurso A, já em 1 toque. O ganho possível é só de rolagem (EF-12). Q12
(Presencial/À distância) também é binária, mas sai com EF-03.

### 9.14 Campos condicionais

Ver a seção 14. Os ramos aparecem no momento certo (na Seção seguinte), e as respostas de
ramos abandonados ficam inativas e reaparecem se a pessoa voltar (006 FR-030; observado na
auditoria mobile-first). O comportamento é previsível. Os complementos são o ponto fraco
(EF-08).

### 9.15 Teclado e entrada mobile

| Campo | `type` / `inputmode` / `autocomplete` | Problema |
|---|---|---|
| CPF | text / numeric / off | Bom (`off` é intencional, por privacidade) |
| Data de nascimento | text / numeric / bday | Dica pede "/", que o teclado numérico do iOS não tem (EF-17) |
| Q3, Q10 | text / — / — | Teclado alfabético para número (EF-15) |
| Complementos | text / — / — | Adequado |
| Nome (declaração) | text / — / — | Falta `autocomplete="name"` (EF-25) |
| Curso (declaração) | text / — / — | Texto livre, sem sugestão; aceitável enquanto não houver catálogo confiável |
| Ano (declaração) | number / numeric | Bom |
| E-mail (020) | email / email / email | Bom |

Enter/"Ir" não envia a Seção (corrigido pela 014). Alvos de toque já auditados (MF-04).

### 9.16 Microcopy

| Texto atual | Problema | Sugestão |
|---|---|---|
| "Indique o questionário que pretende preencher" | Expõe a estrutura; é do instrumento | Sai com EF-03 (D) |
| "Descreva: «Outro»" | Não diz que é preciso marcar "Outro" | "Descreva o que se encaixa em «Outro»", visível só com a opção marcada (EF-08) |
| "Confira os dados abaixo e tente novamente. Conferir os dados" + "Informar minha formação" | Duas saídas sem critério | EF-09 |
| "(obrigatória)" ×50 | Ruído | EF-11 |
| "Sair sem salvar esta seção / O que já foi salvo antes continua guardado." | Pede raciocínio sobre dois tipos de salvamento | EF-22 |
| "Você chegou ao fim da pesquisa." (depois de recusar) | Não é o fim de uma pesquisa respondida | EF-20 (D) |
| Faixa "Ambiente de demonstração… não é autenticação forte." | Só existe na demonstração; não conta | — |

### 9.17 Decisões desnecessárias

Uma decisão é desnecessária quando o sistema poderia tomá-la sozinho, com segurança.

| # | Decisão pedida | O sistema já sabe ou pode decidir? | Achado / grupo |
|---|---|---|---|
| 1 | Q14: qual "questionário" (nível) | Sim, `ConclusaoAcademica.nivel` (vocabulário pendente) | EF-03 · C/D |
| 2 | Q11: campus | Sim, `unidade` | EF-03 · C/D |
| 3 | Q12: modalidade | Sim, `modalidade` | EF-03 · C/D |
| 4 | Q10: ano de conclusão | Sim, `ano_conclusao` | EF-03 · C/D |
| 5 | Q15–Q19: curso | Sim, `curso` | EF-03 · C/D |
| 6 | Q16: forma de oferta | Sim, `forma_oferta` | EF-03 · C/D |
| 7 | Q3: idade | Derivável da data de nascimento (fonte) | EF-15 · C |
| 8 | Q10/Q11/Q14/curso no caminho declarado | Sim, foi declarado minutos antes | EF-04 · D |
| 9 | Q2–Q9 e situação atual na 2ª formação | Sim, respondido na Participação irmã | EF-05 · D |
| 10 | "Conferir" × "Informar formação" | Não sabe, mas pode orientar a ordem | EF-09 · A |
| 11 | Qual formação primeiro | Qualquer ordem serve; a escolha só tem valor se a pessoa preferir | EF-05/EF-06 · A |
| 12 | Marcar "Outro" antes de descrever | O sistema não deve inferir; deve mostrar o campo só depois da escolha | EF-08 · A |
| 13 | "Concluir pesquisa" depois da última Seção | Não. A confirmação de um ato irreversível tem valor | mantida (EF-23 · A) |
| 14 | "Sair sem salvar" × "Salvar e sair" | O caso de descartar é raro | EF-22 · A |
| 15 | Q13: forma de ingresso/cotas | Talvez (fora da 001) | C |

### 9.18 Informação institucional já conhecida

| Pergunta | Fonte possível | Disponível hoje? | Grupo |
|---|---|---|---|
| Q10 ano | `ConclusaoAcademica.ano_conclusao`/`data_conclusao` | Sim, na fonte simulada; real pendente (001/DP-001, DP-004) | C + D (DP-307) |
| Q11 campus | `unidade` | Idem | C + D |
| Q12 modalidade | `modalidade` | Idem; vocabulário pendente (001/DP-007) | C + D |
| Q14 nível/ramo | `nivel` | Idem; vocabulário pendente | C + D |
| Q15–Q19 curso | `curso` | Idem; as listas do formulário são históricas, não catálogo | C + D |
| Q16 forma de oferta | `forma_oferta` | Idem | C + D |
| Q3 idade | Data de nascimento na fonte (usada só para verificação; não fica na Pessoa) | Não como dado analítico | C |
| Q13 ingresso/cotas | Não está na 001 | Não | C |
| Q22–Q24, Q27, Q31, Q32 (extensão, monitoria, estágio, intercâmbio, IC, bolsa) | Registros de Proex/Proen/PRPPG | Não (DP-308) | C |
| Q46/Q49/Q51 (estuda no Ifes agora) | Matrícula ativa na fonte (o cenário tem `matricula_ativa` para Fernanda, mas só Conclusões são incorporadas) | Não | C |
| Q2–Q9 (dados pessoais) | Cadastro acadêmico (gênero, cor/raça, PcD) | Não, e há DP-309 (dados sensíveis) | C + D |

---

## 10. Análise tela a tela

Cada tela passa pelo **teste de 30 segundos**: uma pessoa sem treinamento entende o que se
pergunta, por que, como responder e o que fazer em seguida?

| Tela | O quê | Por quê | Como | Próximo passo | Falhas registradas |
|---|---|---|---|---|---|
| Acesso | Sim | Sim ("registrados no Ifes") | Parcial: a dica de data pede "/" | Sim | EF-17 |
| Não confirmada | Sim | — | — | **Não**: duas saídas sem critério | EF-09 |
| Declaração | Sim | Parcial ("passará por verificação") | Sim | Sim | EF-25 |
| Confirmação da declaração | Sim | Sim | — | Parcial: não há "Corrigir" | EF-25 |
| Suas formações (1 formação) | Sim | Sim ("O Ifes quer saber como sua trajetória seguiu") | Sim | Sim, 1 botão | Sem duração nem tamanho (EF-07) |
| Suas formações (várias) | Sim | Sim | Sim | Parcial: não diz que são N questionários inteiros | EF-05 |
| S1 Termos | Sim | Sim | Sim | **Não em 30 s**: a pergunta está a 1,7 tela | EF-13 |
| S2 Pessoais | Sim | Não (por que o Ifes quer escolaridade dos pais?) | Sim | Sim | EF-11; motivo é do instrumento (D) |
| S3 Curso | **Não**: contradiz o quadro de contexto; Q14 em linguagem interna | **Não** | Sim | Sim | EF-03 |
| S4–S7 Curso | Sim | **Não** (o curso está escrito acima) | Lista longa | Sim | EF-03 |
| S8 Avaliação | Sim | Sim | Parcial: escala sem rótulo do 1; complemento | Sim, mas a 5 telas | EF-08, EF-10, EF-14 |
| S9 Trabalha | Sim | Sim | Sim | Sim, a 5 telas | EF-02 |
| S10 Não trabalha | Sim | Sim | Parcial (complemento) | Sim | EF-08 |
| S11 Estudo | Sim | Sim | Parcial: Q48 com instrução condicional em texto | Sim | EF-16 |
| S12 Estuda | Sim | Sim | Sim | Sim | — |
| S13 (sem título) | Parcial: título genérico "Egresso Ifes", aba "Seção 13" | Sim | Sim | Sim | EF-07 |
| Concluir | Sim | Sim | Sim | Sim, mas abaixo de 6 linhas de contexto | EF-23 |
| Concluída | Sim | — | — | **Não** para quem tem outra formação pendente | EF-06, EF-26 |
| Acesso após sessão expirada | **Não**: nada diz o que aconteceu | **Não** | Sim | Parcial | EF-01 |

---

## 11. Oportunidades de pré-preenchimento

| Pergunta | De onde viria | Natureza | Possível agora? | Risco | Recomendação |
|---|---|---|---|---|---|
| Q10, Q11, Q12, Q14, Q15–Q19, Q16 | Conclusão Acadêmica | Institucional | **Não**: FR-028 da 008, DP-307, princípio III (gravaria institucional como declarado) | Alto | **Não pré-preencher. Retirar da jornada** (EF-03) |
| Mesmas, no caminho declarado | FormacaoDeclarada | Declarado pela mesma pessoa | Tecnicamente sim; a correspondência de vocabulário está pendente | Médio | Esperar a nova Versão (EF-04) |
| Q3 | Data de nascimento | Derivado | Não (a data não é dado analítico da Pessoa) | Alto se gravado como resposta | Derivar na análise, nunca como Resposta (C) |
| Q1, Q2–Q9, Q33–Q40, Q45, Q46, Q49, Q51 na 2ª formação | Participação irmã, mesma Campanha | Declarado | Sim, com decisão | Médio (ancoragem) | Valor inicial visível e editável, com aviso (EF-05) |
| Q2, Q4, Q8, Q9 na Campanha seguinte | Participação anterior | Declarado | Sim, com decisão | Alto (princípio I, comparabilidade) | Só com decisão da CPAEG (EF-21) |
| Qualquer Opção "padrão" | — | — | — | Indução | **Não recomendado** |

---

## 12. Oportunidades de redução de digitação

| Campo | Onde | Obrigatório | Necessário? | Redução |
|---|---|---|---|---|
| CPF (11 dígitos) | Acesso | Sim | Sim (018) | — (aceita só números; manter) |
| Data de nascimento (8 dígitos) | Acesso | Sim | Sim (018) | Dica certa (EF-17) |
| Q3 idade | S2 | Sim | **Não**: derivável | Teclado numérico (B); eliminar (C) |
| Q10 ano | S3 | Sim | **Não**: institucional | Eliminar (C/D) |
| Complemento Q26 / Q32 / Q45 | S8, S10 | Não | Sim, quando "Outro" | Mostrar só com a opção marcada (EF-08) |
| Nome | Declaração | Sim | Sim (validação) | `autocomplete="name"` (EF-25) |
| Curso | Declaração | Sim | Sim (formação não encontrada) | Manter texto livre até haver catálogo confiável; depois, sugestões |
| Ano | Declaração | Sim | Sim | Já numérico |
| E-mail | Pós-conclusão (opcional) | Não | Sim | Já adequado |

Tamanho esperado das respostas: todos os textos do instrumento são curtos e os rótulos
deixam isso claro; não há `textarea`.

---

## 13. Oportunidades de eliminação de interações

**Teste do "por que estou fazendo isso?"**: se a interação fosse removida, que informação,
segurança ou controle se perderia?

| Interação | O que se perde ao remover | Veredito |
|---|---|---|
| Responder Q10–Q19 com Conclusão | Nada para a coleta (já é institucional); perde-se a comparação "declarado × institucional" do ADR 0003 | **Candidata à remoção** (D) |
| Ler o convite de abertura na S1 | Nada: já foi lido antes de "Iniciar" (o texto continua acessível recolhido) | **Recolher** (EF-13) |
| Escolher formação quando há várias | Preferência da pessoa | Manter; acrescentar a ligação depois da conclusão (EF-06) |
| Marcar "Deixar esta pergunta sem resposta" | Desfazer rádio sem JavaScript | Manter |
| "Sair sem salvar esta seção" | Descartar o que foi marcado (raro) | **Candidata à remoção** (EF-22) |
| "Voltar à seção anterior" | Rever respostas | Manter |
| Tela "Concluir a pesquisa" | Revisão e confirmação de ato irreversível | Manter, reordenada (EF-23) |
| Tocar em "Concluir" depois de recusar (Q1 = Não) | Registro da recusa | Depende de EF-20 (D) |
| Confirmação da declaração ("Começar") | Revisão do que foi declarado | Manter; acrescentar "Corrigir" (EF-25) |
| Ir a `/formacoes/` antes de continuar, na retomada | Contexto | Manter, mas dizer onde parou (EF-19) |
| Reidentificar após sessão expirada e refazer a Seção | Segurança (reidentificar); nada (refazer) | Manter a reidentificação; **eliminar o refazer** (EF-01) |

---

## 14. Condicionais e divulgação progressiva

| Condicional | Mecanismo | Momento | Relação visual | Mudança de resposta | Avaliação |
|---|---|---|---|---|---|
| Q1 → S2 ou fim | Regra (006) | Ao enviar S1 | Seção seguinte | Volta a S1 e muda: percurso recalculado | Previsível; consequência não explicada (EF-20) |
| Q14 → S4/S5/S6/S7 | Regra | Ao enviar S3 | Seção seguinte | Resposta do ramo antigo fica inativa e reaparece se voltar | Previsível; a decisão em si é desnecessária (EF-03) |
| Q33 → S9/S10 | Regra | Ao enviar S8 | Seção seguinte | Idem | Bom; Q33 deveria abrir o bloco (EF-10) |
| Q46 → S12/S13 | Regra, com Q47/Q48 depois na mesma Seção (DP-302) | Ao enviar S11 | Seção seguinte | Idem | Aceitável |
| Q5 → Q6 | **Só textual** ("Se sim") | Sempre visível | Pergunta seguinte | Nada muda | Lacuna (EF-16, DP-303) |
| Q47 → Q48 | **Só textual** | Sempre visível | Pergunta seguinte | Nada muda | Lacuna (EF-16, DP-302) |
| "Outro" → complemento | Validação de forma | Sempre visível; erro só no envio | Abaixo das Opções | Desmarcar com texto preenchido gera erro | **Principal lacuna da interface** (EF-08) |

Não se recomenda transformar a Seção em formulário dinâmico com JavaScript. Os
condicionais por Seção são estáveis e previsíveis. Dentro da Seção, CSS `:has()` basta para
os casos decididos, e sem ele o comportamento é o atual.

---

## 15. Erros e recuperação

| Situação | Quando é detectado | Perda de dados | Mensagem explica a correção? | Campo evidente? | Prevenível? |
|---|---|---|---|---|---|
| Obrigatória sem resposta | Ao enviar a Seção | **Não**: o restante é gravado [obs] | Sim ("Ainda faltam estas perguntas") | Sim, link com âncora | Não precisa (é progresso, não erro) |
| Complemento sem Opção | Ao enviar | **Sim, a Seção inteira não é gravada** (os valores reaparecem na tela) [obs] | Sim ("Para descrever, marque a opção «Outro»") | Sim, mas a 3 telas do resumo | **Sim** (EF-08) |
| Opção forjada / escala fora | Ao enviar | Seção inteira | Sim | Sim | Só ocorre com envio forjado |
| CPF/data em formato inválido | Ao enviar o acesso | Não (campos mantidos) | Parcial ("Confira o CPF informado") | Sim | Dica certa (EF-17) |
| CPF/data não confirmados | Ao enviar | Não | Parcial (EF-09) | — | Orientação (EF-09) |
| Declaração inválida (ano futuro, campo vazio) | Ao enviar | Não | Sim | Sim | Sim (`max` no ano já existe) |
| Sessão expirada | Ao enviar | **Sim, a Seção** | **Nenhuma mensagem** | — | Sim (EF-01) |
| Selo da declaração vencido | Ao enviar | **Sim, o formulário** | **Nenhuma mensagem** | — | Sim (EF-18) |
| Falha de CSRF (cookie perdido) | Ao enviar | Sim, a Seção | "Volte à página anterior e envie novamente" | — | Raro; sem ação |
| Rede caiu durante o envio | — | Nunca duplica (MF, [obs] na época) | Mensagem do navegador | — | Fora do escopo |
| Respostas contraditórias ("Não houve" + "Artigos") | Nunca | — | — | — | Capacidade nova (EF-24) |

No celular, o padrão "resumo no topo, campo no fim" custa uma rolagem de até 5 telas quando
o erro está no fim da S8. A âncora do resumo resolve com um toque; só é preciso perceber
que é um link.

---

## 16. Interrupção e retomada

| Situação | O que acontece | O que a pessoa entende | Evidência |
|---|---|---|---|
| Trocar de aba ou app por pouco tempo | Nada se perde se a aba não for descartada | — | [cód] |
| Trocar de app e o sistema descartar a aba | Seção não enviada perdida | Nada; ao voltar, os campos estão vazios | MF-01 [obs na época] |
| Recarregar | Seção não enviada perdida | Nada | MF-01 |
| Ficar mais de 30 min parado e enviar | **Seção perdida e volta ao CPF sem aviso** | **Nada** | EF-01 [obs] |
| Fechar o navegador | Sessão encerrada (`SESSION_EXPIRE_AT_BROWSER_CLOSE`); o que foi salvo permanece | Precisa reidentificar | [cód] |
| Mais de 8 h desde a confirmação | Sessão encerrada | Idem | [cód] |
| "Salvar e sair" | Grava o respondido; aviso "O que você respondeu nesta seção está salvo" | Bom | [cód; mensagens] |
| "Sair sem salvar" | Descarta o não enviado; nota explica | Exige raciocínio (EF-22) | [obs] |
| Voltar outro dia | CPF + data → "Continuar a pesquisa" → Seção atual | Não sabe onde parou nem quanto falta | [obs] (EF-19) |
| Perder a conexão no envio | Grava ou não, sem duplicar | Mensagem do navegador | MF [obs na época] |
| Declarante: selo vence (30 min) | Volta ao acesso sem aviso; declaração perdida | Nada | EF-18 [cód] |

**Precisa completar tudo de uma vez?** Não. Pode parar entre Seções sem perda, e isso é
dito na entrada. Dentro de uma Seção, a interrupção ainda é cara (S8/S9). O maior risco é
a expiração silenciosa.

---

## 17. Quick wins

Ordenados pela relação entre redução de esforço e custo. Todos ficam nos grupos A ou B
pequeno, e nenhum altera o instrumento.

| # | Mudança | Achado | Elimina | Custo |
|---|---|---|---|---|
| 1 | Na confirmação, ligação direta para a próxima formação pendente | EF-06 | Descobrir o caminho; risco de não responder a 2ª formação | PP |
| 2 | Aviso de sessão expirada e retorno direto à Seção | EF-01 (1, 2) | Dúvida, 2 toques; não elimina a perda (ver item B) | PP–P |
| 3 | Complemento "Outro" visível só com a opção marcada (CSS `:has()`) | EF-08 | O único erro de forma; a recusa da Seção mais longa | PP |
| 4 | Tela "Não foi possível confirmar" em 2 passos ordenados; esconder "Continuar para suas formações" após uma falha | EF-09 | Decisão às cegas; declarações desnecessárias | PP |
| 5 | "(opcional)" nas 4 opcionais em vez de "(obrigatória)" nas 50 | EF-11 | Ruído; cerca de 1 tela de rolagem | PP |
| 6 | Convite de abertura recolhido em "Sobre esta pesquisa" | EF-13 | ~1 000 px antes da primeira pergunta | PP |
| 7 | Sim/Não lado a lado | EF-12 | ~0,8 tela de rolagem no cenário A | PP |
| 8 | Dica da data "Só os números, como 12041998" | EF-17 | Procurar a "/" no teclado | PP |
| 9 | "Onde você parou" na tela de formações | EF-19 | Incerteza na retomada | PP |
| 10 | Título de aba/revisão sem "Seção 13"; "Parte anterior salva." | EF-07, 9.11 | Dúvida "salvou?"; linguagem interna | PP |
| 11 | Ordem da tela Concluir e da confirmação final | EF-23, EF-26 | ~1 tela de rolagem em cada uma | PP |
| 12 | Aviso de selo vencido na declaração | EF-18 | Perda silenciosa | PP |
| 13 | Retirar "Sair sem salvar esta seção" | EF-22 | Uma decisão por Seção | PP |
| 14 | "Salvar e continuar depois" também no meio das Seções com mais de 8 perguntas | EF-02 | Metade do risco de perda nas S8/S9 | PP |

---

## 18. Melhorias dependentes de integração acadêmica

Grupo C. Nada aqui está disponível em produção. As fontes reais estão no Portão A
(001/DP-001, DP-004, DP-007).

| Melhoria | Depende de | Perguntas afetadas | Ganho no cenário A |
|---|---|---|---|
| Contextualizar a formação em vez de perguntar | Fonte real com curso, unidade, nível, modalidade, forma de oferta e ano de qualidade suficiente; vocabulário canônico; **e** DP-307 (D) | Q10, Q11, Q12, Q14, Q15–Q19, Q16 | −5 a −6 perguntas, −1 Seção, −2 listas longas, −1 campo de texto |
| Idade derivada | Data de nascimento como dado analítico derivado (proporcionalidade, XVI) | Q3 | −1 campo de texto |
| Forma de ingresso/cotas | Novo atributo na fronteira acadêmica | Q13 | −1 pergunta |
| Experiências durante o curso | Registros de extensão, monitoria, estágio, IC, bolsas (DP-308) | Q22–Q24, Q27, Q31, Q32 | até −6, se a qualidade permitir; senão, "confirmar" em vez de "perguntar" |
| Estudo atual no Ifes | Matrículas ativas na fronteira acadêmica | Q46, Q49, Q51 (parcial) | −1 a −3 para quem estuda no Ifes |
| Dados pessoais cadastrais | Cadastro acadêmico; DP-309 | Q2, Q4, Q5 | Não recomendado sem decisão sobre dados sensíveis |

---

## 19. Orçamento de interação projetado

Cenário A (Ana), celular 375×812. A coluna do meio não muda o instrumento; a da direita
supõe a nova Versão contextualizada (DP-307 decidida e fonte real), sem os itens da DP-308.

| Métrica | Atual | Após A+B (sem mudar o instrumento) | Após C+D (Versão contextualizada) |
|---|---:|---:|---:|
| Passos/telas (carregamentos) | 12 | 12 | 10–11 |
| Seções | 8 | 8 | 6–7 |
| Perguntas visíveis | 46 | 46 | 40 |
| Campos digitáveis obrigatórios (acesso + instrumento) | 4 | 4 (2 com teclado numérico) | 2 |
| Teclas digitadas | ~25 | ~25 | ~19 |
| Listas suspensas | 4 | 4 | 2 |
| Decisões explícitas | ~44 | ~44 | ~38 |
| Cliques/toques estimados | ~62 | ~60 | ~50 |
| Rolagem (telas de 812 px) | ~27,6 | ~24 | ~20 |
| Erros de forma possíveis no percurso | 2 (Q26, Q32) | 0 com `:has()` | 0 |
| Perda silenciosa por sessão expirada | Sim | Não | Não |

**Outros cenários:**

| Métrica | Atual | Após A+B | Após C+D |
|---|---:|---:|---:|
| Cenário C: campos digitáveis obrigatórios | 7 | 7 | 5 |
| Cenário C: dados informados duas vezes | 4 | 4 | 0 |
| 2ª formação (Bruno): perguntas novas | 46 | 46 | ~40; **~20 com reaproveitamento (EF-05, D)** |
| Retomada após expiração: telas até voltar à Seção | 3 (acesso, formações, Seção vazia) | 2 (acesso, Seção) | 2 |

Os números de A+B mostram o que esta auditoria quer deixar claro: **sem mudar o instrumento,
a quantidade de trabalho cai pouco (cerca de 3 a 10%)**. O que cai muito é o trabalho
desperdiçado: erros, perdas e desorientação. As grandes reduções de perguntas e digitação
dependem de C e D.

---

## 20. Jornada proposta

Sem mudar o instrumento (A+B):

```
/acesso/  "Só os números" ─┬─ confirmada ─▶ /formacoes/ (onde parou · faltam no máximo N) ─▶ Seção atual
                           └─ não confirmada ─▶ 1. Conferir os dados  2. Informar minha formação
S1  [Sobre esta pesquisa ▸] termo + Q1                         Parte 1 · faltam no máximo 7
S2  "(opcional)" só em Q6; Sim/Não lado a lado                 "Parte anterior salva."
…   complemento só com "Outro" marcado; "Salvar e continuar depois" no meio de S8/S9
Concluir: aviso + botão primeiro; revisão e contexto depois
Concluída: [Responder sobre {outra formação}] → Minha trajetória → e-mail
Sessão expirada: "Por segurança…" → confirmar → volta à mesma Seção, com o que estava marcado (EF-01.3)
```

Com a nova Versão contextualizada (C+D):

```
/formacoes/ "Esta pesquisa é sobre TADS · Serra · 2022"
Termo → Sobre você (Q2–Q9, Q13) → Durante o curso (Q20–Q32) → Trabalho (Q33 → …) → Estudos (Q46 → …) → Fechamento (Q52–Q54)
Ramos por nível institucional (sem Q14); curso, campus, ano e modalidade só como contexto.
2ª formação: perguntas sobre você e o presente chegam preenchidas e editáveis (se decidido).
```

---

## 21. Riscos e trade-offs

| Proposta | Benefício | Risco | Mitigação |
|---|---|---|---|
| Retirar Q10–Q19 (EF-03) | Maior redução de esforço; coerência | Comparabilidade com 2024; perda da medida da divergência (ADR 0003); dependência de fonte com qualidade desconhecida | Nova Versão explícita (VIII); exportação marca a origem (institucional × declarado); manter a divergência mensurável onde houver dado de 2024 |
| Reaproveitar respostas entre formações e Campanhas (EF-05, EF-21) | −20 perguntas por formação extra | Ancoragem (confirmar sem ler); princípio I | Só valor inicial visível e editável, com aviso; nunca cópia silenciosa; restrito à mesma Campanha num primeiro momento |
| Sessão mais longa (EF-01.4) | Menos expiração | Computadores compartilhados | Aviso + preservação (EF-01.3) em vez de prolongar |
| Melhoria progressiva com `sessionStorage` (EF-02) | Recarregar não perde a Seção | Contraria a exclusão da 014; resposta em claro no aparelho | Só a Seção aberta, apagada ao enviar; decisão explícita |
| `:has()` para complemento (EF-08) | Fim do erro de forma | Navegador antigo mostra o campo (comportamento atual) | Degradação graciosa |
| Indicador "faltam no máximo N" (EF-07) | Horizonte | Parecer impreciso quando o ramo encurta | Formular sempre como máximo, nunca percentual |
| Ocultar Q6 / Q48 (EF-16) | Menos leitura | Muda quem vê a pergunta | Só com DP-303/DP-302 decididas |
| Recolher o convite (EF-13) | Pergunta mais perto | Menor leitura do convite | O texto continua apresentado; o termo segue visível |

Nenhuma proposta deste documento cria dark pattern, gamificação, animação, SPA ou
dependência de JavaScript.

---

## 22. Recomendação de implementação

**Duas frentes independentes:**

1. **Uma feature de UX, grupos A e B, sem tocar o instrumento** (proposta de nome
   abaixo). Ela resolve os dois P0 no que cabe à interface e os P1 que não dependem de
   decisão (EF-06, EF-07, EF-08, EF-09), mais os quick wins. Pode ser feita já, com a
   baseline e a fonte simulada, e cada item é verificável por teste.
2. **Um pacote de decisões para a CPAEG**, que alimenta a nova Versão já prevista no
   roadmap: DP-307 (EF-03 e EF-04), reaproveitamento entre formações (EF-05) e entre
   Campanhas (EF-21), DP-301 (EF-14), DP-302/DP-303 (EF-16), tratamento da recusa (EF-20),
   opções exclusivas (EF-24) e a fronteira da S8 (EF-10). A engenharia correspondente é
   pequena **depois** das decisões. Hoje, o gargalo é a decisão, não o código.

**Ordem sugerida na feature de UX:** EF-01 (aviso e retorno), EF-06, EF-08, EF-09 → EF-07
(indicador) → quick wins de rolagem (EF-11, EF-12, EF-13) → EF-01.3 (preservar o envio) →
o restante.

**Não fazer agora:** pré-preencher Q10–Q19 a partir da Conclusão; autocomplete de curso;
autosave sem decisão sobre a exclusão da 014; qualquer default de resposta.

### Próxima feature recomendada (só nome e escopo; não criada)

**023 — Jornada de resposta com menos esforço (sem mudar o instrumento)**

- **Inclui:** aviso de sessão expirada, retorno à Seção e preservação do envio expirado
  (EF-01); lembrete de salvar no meio das Seções longas (EF-02); ligação para a próxima
  formação pendente (EF-06); indicador "parte X · faltam no máximo N" e títulos sem
  "Seção N" (EF-07); complemento condicionado por CSS (EF-08); tela de não confirmação
  orientada (EF-09); "(opcional)" (EF-11); Sim/Não lado a lado (EF-12); convite recolhido
  (EF-13); dica da data (EF-17); aviso de selo vencido (EF-18); "onde você parou" (EF-19);
  rodapé de Seção, tela Concluir e confirmação reordenados (EF-22, EF-23, EF-26); ajustes
  da declaração (EF-25).
- **Não inclui:** nenhuma mudança em Pergunta, Opção, Seção, regra ou obrigatoriedade; nada
  de DP-30x; reaproveitamento de respostas; JavaScript obrigatório.
- **Decisões a tomar na spec:** se a preservação do envio expirado (EF-01.3) entra; se a
  melhoria progressiva de EF-02 entra (revisando a exclusão da 014); se o complemento oculto
  e desmarcado deve ser ignorado (EF-08, 005 FR-030).
- **Critério de sucesso sugerido:** cenário A com 0 erros de forma possíveis, 0 perdas
  silenciosas, rolagem ≤ 24 telas e resposta "sim" no teste de 30 segundos em todas as
  telas, exceto S3/S4–S7 (que dependem da nova Versão).

---

## Anexo — Evidências

Capturas em 375×812, cenário de demonstração, pasta
[`evidencias-esforco/`](evidencias-esforco/):

| Arquivo | Conteúdo |
|---|---|
| 01-acesso | Entrada (CPF e data) |
| 02-formacoes-ana | Uma formação, "Iniciar a pesquisa" |
| 03-secao1-topo · 04-secao1-pergunta | Convite reapresentado; a pergunta só depois de ~1,7 tela |
| 05-secao3-contexto-e-perguntas | Contexto "Serra · 2022" e, abaixo, ano e campus perguntados |
| 06-secao6-curso | Curso numa lista de 50 |
| 07-secao8-topo | Seção de 14 perguntas; escala só com "5 = Concordo totalmente" |
| 08-secao8-nao-houve-e-artigos | Opções contraditórias aceitas; complemento preenchido |
| 09-secao8-erro-complemento | A Seção inteira recusada |
| 10-concluir-contexto | Unidade, data, nível e modalidade institucionais na conclusão |
| 11-concluida | Confirmação; ação principal abaixo da dobra |
| 12-sessao-expirada-acesso | Volta à entrada sem mensagem após a expiração |
| 13-retomada | "Continuar a pesquisa" sem dizer onde parou |
| 14-nao-confirmada | Duas saídas sem critério |
| 15-declaracao-formulario · 16-declaracao-confirmacao | Declaração da formação |
| 17-declarada-secao3 | Ano e campus perguntados de novo depois da declaração |
| 18-selecao-bruno | "Cada formação tem sua própria pesquisa" |

**Ambiente usado:** banco local `trajetoria_esforco` (dados fictícios) e `.env` local
(ignorado pelo Git), criados só para esta auditoria, seguindo o
[ambiente local](../desenvolvimento/ambiente-local.md). Nenhum código da aplicação foi
alterado. Para o teste de EF-01, o servidor foi iniciado com
`TRAJETORIA_SESSAO_INATIVIDADE=1` e depois reiniciado com o padrão.
