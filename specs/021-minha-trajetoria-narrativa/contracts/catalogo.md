# Contrato: catálogo fechado de formulações

Este contrato cobre os FR-022 a FR-025 e o FR-061. As formulações ficam em
`trajetoria/narrativa/catalogo.py`. O texto pode ser revisto sem mudar comportamento
(DP-801). As condições, não.

## Convenções

- Placeholders nomeados: `{curso}`, `{unidade}`, `{ano}`, `{n}`, `{nome}`, `{apuracao}`.
- **Uma formulação só é usada quando todos os seus placeholders têm valor.** Se faltar
  algum, usa-se a variante sem ele. Se não houver variante, a frase não aparece.
- A unidade é escrita como a fonte a informa, sempre como "na unidade {unidade}", nunca
  com "Campus" acrescentado (FR-017).
- Singular e plural são escolhidos por `{n}`.

## Formulações (P1)

| Chave | Condição | Texto (proposta) |
|---|---|---|
| `registradas` | sempre que houver formação | "O Ifes registra {n} formação concluída por você." / "O Ifes registra {n} formações concluídas por você." |
| `nome_registros` | nome presente | "Registros de {nome}" (subtítulo discreto da seção 1) |
| `concluiu_completo` | curso, unidade e ano | "Em {ano}, você concluiu {curso} na unidade {unidade}." |
| `concluiu_sem_unidade` | curso e ano | "Em {ano}, você concluiu {curso}." |
| `concluiu_sem_ano` | curso e unidade | "Você concluiu {curso} na unidade {unidade}." |
| `concluiu_so_curso` | só curso | "Você concluiu {curso}." |
| `formacao_sem_curso` | sem curso | nenhuma frase; o item da lista mostra só os atributos presentes |
| `depois` | research R5 | "Depois dessa formação, você também concluiu {curso}." |
| `ha_anos` | data de conclusão e N ≥ 1 | "Há {n} ano desde essa conclusão." / "Há {n} anos desde essa conclusão." |
| `desde` | só ano | "Concluída em {ano}." |
| `card_mais` | mais de 4 formações no card | "e mais {n} formação registrada" / "e mais {n} formações registradas" |
| `card_rodape` | sempre | "Instituto Federal do Espírito Santo" (o título do card já diz "Minha trajetória no Ifes") |
| `card_demo` | demonstração | "Demonstração — dados fictícios" |

Na formulação `desde`, "desde AAAA" do FR-020 vira um rótulo neutro de ano. Um texto
como "desde 2022, muita coisa mudou" afirmaria algo sem fonte.

## Formulações (P2)

| Chave | Condição | Texto (proposta) |
|---|---|---|
| `inicio` | ingresso coerente, menor ano de ingresso único (FR-050) | "Sua trajetória no Ifes começou em {ano}, em {curso}." |
| `agregado_curso` | métrica 1 selecionada | "Em {ano}, {n} conclusões de {curso} foram registradas na unidade {unidade}, incluindo a sua." (com N = 1: "Em {ano}, 1 conclusão de {curso} foi registrada na unidade {unidade}: a sua.") |
| `agregado_unidade` | métrica 2 selecionada | "Em {ano}, {n} conclusões foram registradas na unidade {unidade}." |
| `apuracao` | junto de cada agregado | "Dados institucionais apurados em {apuracao}." |

## Formulações do card editorial (revisão de 2026-10-05; FR-078, FR-079)

No card, as contagens aparecem decompostas em **número + rótulo**, com a mesma semântica
das formulações P2. Na página continua a frase completa.

| Chave | Condição | Texto (proposta) |
|---|---|---|
| `destaque_curso` | métrica 1 no card | número `{n}`; rótulo "conclusão deste curso" / "conclusões deste curso" e "na unidade {unidade} em {ano}" |
| `destaque_unidade` | métrica 2 no card | número `{n}`; rótulo "conclusão registrada" / "conclusões registradas" e "na unidade {unidade} em {ano}" |
| `card_apuracao` | rodapé do card, com destaque | "Dados institucionais apurados em {apuracao}." |
| `legenda_imagem` | sempre | "Unidade {unidade} · {tipo}"; sem unidade: "Ifes · {tipo}" (`tipo` = ilustração ou fotografia) |
| `fecho` | sempre | "Essa história também é minha." |
| `hashtag` | sempre | "#SouEgressoIfes" |
| `capitulo` | página, com 2 ou mais capítulos | "Capítulo {k} de {total}" |

Títulos de capítulo da página: "Sua formação", "Sua continuidade no Ifes", "Naquele ano no
Ifes" e "Seu card". Eles substituem os títulos de seção anteriores. Rótulos de cartão sem
número e sem verbo continuam vinculados à semântica do FR-061: o sujeito é "conclusões" e
nunca pessoas.

## Formulações vedadas (teste de varredura)

O texto renderizado da página e do card, em todos os cenários simulados de P1 e P2, NÃO
DEVE conter (sem diferenciar maiúsculas):

- **Ingresso sem dado:** "tudo começou" e "começou em" sem o complemento de ingresso.
- **Grupos de pessoas:** "turma", "geração", "coorte", "colegas", "se formaram com você",
  "formaram com você".
- **Termos de matrícula e de egresso:** "matriculad", "ingressantes", "estudantes", "alunos",
  "egressos" (este último aplicado a contagens).
- **Comparações e taxas:** "%", "taxa", "mais que", "melhores", "entre os".
- **Afirmações sem fonte:** "época especial", "viveu".
- **Indicador da PAEG:** "verticaliza".
- **Prefixo de unidade:** "Campus", exceto quando fizer parte do valor da unidade
  informado pela fonte.

Varrer palavras é um teste de rede de segurança: pega o erro grosseiro. A garantia
principal vem de outro teste, que verifica que **toda frase emitida é uma formulação do
catálogo** preenchida com valores da entrada.
