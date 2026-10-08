# Research — Feature 025: Oportunidades curadas do Portal do Egresso

**Data:** 2026-10-08.

**Base:** `main` com a 024 integrada e os ajustes da 024 pós-avaliação por IA (PR #47).

**Situação:** só plan. A antecipação está autorizada no roadmap (Revisão 4). Código e migrações
aguardam a leitura do Checkpoint 1. O Checkpoint 1 continua **NÃO APLICADO**.

Cada item traz a decisão, o motivo e as alternativas avaliadas.

---

## R1 — Onde a Oportunidade vive

**Decisão.** Tudo fica dentro do app `trajetoria/portal`. Não há app novo.
- O modelo fica em `portal/models.py` e a migração é a primeira do app (`0001_oportunidade`).
- A regra, as operações, a pertinência, as views e os templates ficam no subpacote
  `portal/oportunidades/`.

**Motivo.**
- A spec escolheu a alternativa A ("Modularização"): o fato existe só para o Portal.
  Desligar a camada tira a página do egresso e a curadoria juntas.
- O teste de fronteira que já existe ("o núcleo não cita o Portal") continua valendo sem
  mudança.

**Revisa a 024.** O teste `test_portal_sem_modelo_nem_migracao` (024 FR-029) passa a exigir:
- exatamente um modelo, `Oportunidade`;
- migrações só aditivas;
- nenhuma chave estrangeira para tabelas do núcleo.

**Alternativas.**
- **App `oportunidades` separado.** Rejeitado: a varredura de fronteira o trataria como
  núcleo, e seria preciso redefinir a camada.
- **Modelo no núcleo.** Vetado pela Constituição 2.1.0.

## R2 — Regra de curadoria fora do módulo de governança

**Decisão.** A regra nomeada `pode_curar_oportunidades(vinculos)` e o escopo de administração
ficam em `portal/oportunidades/governanca.py`. Eles são construídos só com primitivas da 010:
`Papel`, os vínculos ativos e `escopo_de_acompanhamento`, cuja semântica é a mesma (a CPAEG
vence e é institucional; as CSAEG somam unidades).

**Motivo.**
- O núcleo não pode conhecer competências da camada.
- O teste `tests/governanca/test_governanca_fronteiras.py` congela o conjunto de regras do
  núcleo.
- A convenção da 010 continua respeitada: uma regra nomeada por ação, sem motor de políticas
  (010 FR-034). Muda só o lugar da regra.

**Alternativa.** Uma regra em `governanca/regras.py`. Rejeitada: acoplaria o núcleo à camada
e exigiria revisar a fronteira da 010.

## R3 — Entrada do operador na curadoria

**Decisão.** O mapa fechado de destinos da escolha de operador (`demonstracao/views.py`,
`_DESTINOS`) passa a ter um ponto de extensão neutro, `registrar_destino(chave, endereco)`.
- O `PortalConfig.ready()` registra `"curadoria"` → `/curadoria/oportunidades/` **sempre**,
  com um predicado de ativação:
  `registrar_destino("curadoria", "/curadoria/oportunidades/", ativo=lambda: settings.TRAJETORIA_PORTAL)`.
- O mapa só aceita o destino se `ativo()` for verdadeiro **no pedido**, como o provedor da
  navegação, que relê a configuração a cada pedido (024). Com o Portal desligado,
  `?destino=curadoria` é ignorado e a escolha cai no padrão (`/editor/`). *(Revisado em
  2026-10-08, depois do `/speckit-analyze`: um registro feito só na inicialização não
  acompanharia o Portal desligado em tempo de execução.)*
- Sem operador, a curadoria redireciona para `/demonstracao/operador/?destino=curadoria`.

**Motivo.** É o mesmo padrão do 011 R13: um destino fechado, nunca um endereço do cliente. O
núcleo continua sem citar a camada.

**Alternativas.**
- **Link no painel do acompanhamento.** Rejeitado: o núcleo passaria a apontar para a camada.
- **Página de "escolha um operador" própria do Portal.** Rejeitada: duplicaria a escolha da
  010.

## R4 — Catálogo fictício na preparação da demonstração

**Decisão.** `demonstracao/cenario.preparar()` envia, no fim da transação, o sinal neutro
`cenario_preparado` (`demonstracao/sinais.py`). O Portal conecta um receptor que carrega o
catálogo de forma idempotente, com identificadores fixos (`uuid5`).

**Motivo.**
- O 024 R13 manteve o `preparar_demonstracao` sem mudança, e o núcleo não pode importar o
  Portal.
- O sinal é o mecanismo neutro padrão do Django. O emissor não conhece os receptores.

**Alternativas.**
- **Comando separado (`preparar_oportunidades`).** Rejeitado: seria um passo a mais no
  ambiente local, fácil de esquecer.
- **Importar o Portal no cenário.** Vetado pela fronteira.

**Nota.** O catálogo é carregado com o Portal ligado ou desligado, porque o app está sempre
instalado. Isso é inofensivo: sem o Portal, nenhuma tela o mostra (FR-039).

## R5 — Estados e datas

**Decisão.** O estado é a função pura `estado(oportunidade, hoje)` (spec, "Estados de
publicação").
- `hoje` vem de `timezone.localdate()` na view. Os testes passam `hoje`, como em
  `campanha.consultas.estado`.
- A consulta "em divulgação" filtra
  `publicada_em IS NOT NULL AND retirada_em IS NULL AND inicio <= hoje <= fim`.
- Nenhum processo agendado.

**Escritas.** Ficam em `operacoes.py` (único caminho de escrita), sob `select_for_update`.
- Cada operação revalida o estado e o escopo no momento da escrita.
- A recusa vira `OportunidadeRejeitada(Motivo)`. A view a traduz em erro de campo (422) ou em
  página de conflito (409), como na 017.

## R6 — Validação do endereço oficial

**Decisão.** O endereço é validado por uma função pura em `regras.py`, com `urllib.parse` e
`ipaddress` da biblioteca padrão. Ela recusa:
- esquema diferente de `https`;
- endereço sem nome de máquina;
- usuário ou senha embutidos;
- número IP (v4 ou v6) como destino;
- espaços ou caracteres de controle;
- mais de 500 caracteres.

**Classificação, só para exibição.**
- "site do Ifes" quando o nome de máquina é `ifes.edu.br` ou termina em `.ifes.edu.br`;
- "site externo" nos demais casos.

O domínio exibido é o nome de máquina em minúsculas, sem `www.` removido.

**Fora:**
- consulta de rede ou DNS;
- lista de domínios (DP-2504);
- encurtadores detectados.

## R7 — Pertinência e explicação

**Decisão.** A pertinência é a função pura `pertinentes(oportunidades, conclusoes)` em
`pertinencia.py`.
- Entrada: as oportunidades em divulgação e as Conclusões da Pessoa, na ordem da 007 (o
  `Meta.ordering` do modelo).
- Saída: itens com o grupo, as formações que satisfazem e a explicação.

**Regra.**
- Cada critério definido é testado **na mesma Conclusão**, por igualdade exata. O valor
  `NULL` não satisfaz.
- A oportunidade aparece uma vez.
- Ordem: grupo ("Pela sua formação" → "Para todos os egressos"), depois `inicio` decrescente,
  depois `titulo`, e por fim `id` só para determinismo.

**Explicação.** Os textos ficam em `mensagens.py`; os modelos estão em
[contracts/pertinencia.md](contracts/pertinencia.md).
- **Todos os critérios definidos são citados** (FR-013). *(Revisado em 2026-10-08.)* Cada
  formação é descrita com o valor que satisfaz cada critério: curso, nível ("formação de
  …") e unidade ("na unidade …"). A versão anterior citava só a formação quando havia
  critério de curso e podia omitir nível e unidade exigidos pelo público.
- A unidade aparece como "unidade X", não "campus X". É o vocabulário da 021 e da 024, e o
  Cefor não é campus.
- A unidade responsável aparece numa linha própria, "Oferecida pela unidade X" ou "Oferecida
  pelo Ifes", que acompanha o item na página e no Início. Isso atende ao FR-013 (citar a
  unidade responsável quando ela não é a da formação) sem repetir a informação na
  explicação.

**Fora:** pontuação, peso por critério, histórico.

## R8 — Opções do público e da unidade responsável

**Decisão.**
- Os valores de curso, nível e unidade oferecidos ao operador são os distintos, não nulos,
  das `ConclusaoAcademica`, em ordem alfabética, como estão escritos.
- Para a CPAEG, as unidades responsáveis são esses valores mais "Ifes (institucional)". Para
  a CSAEG, só as unidades dos seus vínculos.
- A marcação usa caixas de seleção, sem JavaScript.

**Limite registrado.** Na fonte real, a lista de cursos pode ter centenas de valores. Isso não
é resolvido aqui: filtro ou agrupamento por unidade fica para quando houver volume real
(Princípio XXII), e o risco fica no plan.

**Alternativa.** Reaproveitar `declaracao.consultas.opcoes_de_unidade`. Rejeitada: ela inclui
os critérios de Campanha, e a ADR 0004 separa abrangência de público.

## R9 — Início: bloco e limite de deslocamento do convite

**Decisão.** O bloco fica entre "O que você pode fazer" e o convite (025 FR-021). Ele tem:
- um `h2` "Oportunidades";
- **um** destaque: o título como link oficial, a explicação e uma linha com a unidade
  responsável e a origem do site;
- o link "Ver as N oportunidades", ou "Ver a página de Oportunidades" quando N = 1.

**Orçamento de altura** a 375 px, fonte a 100%: até 270 px (025 SC-008), estimado assim:

| Elemento | Altura estimada |
|---|---|
| `h2` com margens | ≈ 60 px |
| Título | 2 linhas, ≈ 50 px |
| Explicação | 2 a 3 linhas, ≈ 72 px |
| Origem | 1 linha, ≈ 24 px |
| Link | 44 px |

A soma é ≈ 250–270 px.

**Se a medida passar de 270 px: compactar, nunca omitir.** *(Revisado em 2026-10-08, na revisão
do plan.)* A versão anterior previa tirar a linha de origem do Início. Isso violaria o FR-004
(domínio e classificação do site junto do link) e o FR-013 (unidade responsável), e foi
descartado. As etapas, aplicadas em ordem até caber, todas com tokens da 015:

1. **Margens internas.** `--espaco-1` entre os parágrafos do destaque, em vez da margem
   padrão de parágrafo.
2. **Tipo menor.** Explicação e origem em `--fonte-5` (15 px), com `--entrelinha-enunciado`
   (1,4). O título continua em `--fonte-4`.
3. **Um parágrafo só.** Explicação e origem viram um único parágrafo; a origem é a segunda
   frase. Isso economiza uma margem.

Nenhuma etapa remove o título, a explicação completa, a unidade responsável, a
classificação do site ou o domínio. Se ainda passar de 270 px, a implementação **para** e o
caso volta ao solicitante, para revisar o FR-021 ou o SC-008. Não há corte silencioso de
informação.

A medida é feita na validação, com Ana, Maria e Diego, a 375×812 e fonte a 100%. O destaque
mais longo do oráculo é o O6 de Diego.

**Interpretação do SC-008.** "Em relação à mesma persona sem o bloco" compara o Início com a
navegação de cinco itens, com e sem o bloco. A quebra da navegação é medida à parte, pelo
critério de dobra (h1 e síntese acima da dobra; R10).

## R10 — Navegação com cinco itens (A5 da avaliação por IA)

**Decisão.**
- O item "Oportunidades" fica entre "Minha trajetória" e "Pesquisa", com a mesma condição de
  "Minha trajetória" (`elegivel`), calculada uma vez.
- A largura de cada item fica **independente do estado "atual"**. O include
  `interface/_navegacao.html` (núcleo, neutro) recebe `data-rotulo`. O CSS reserva a largura
  do rótulo em negrito com `::after { content: attr(data-rotulo); font-weight: …; height: 0;
  visibility: hidden; display: block }`.
- Com larguras estáveis, a quebra é a mesma em todas as páginas.

**Esperado, a confirmar na validação:**
- a 375 px e fonte a 100%: duas linhas em todas as páginas com navegação;
- a 320 px e fonte a 200%: um item por linha;
- nenhuma rolagem horizontal;
- `h1` e síntese do Início acima da dobra a 375×812 (024 SC-004).

**Alternativas.**
- **Rótulos mais curtos.** Rejeitado: "Minha trajetória" e "Meu e-mail" estão no teste do
  Checkpoint 1.
- **Menu recolhível.** Exige JavaScript ou o padrão `details`, e esconde destinos.
- **Rolagem horizontal da navegação.** Vetada pelo FR-025 da 024.

## R11 — Vocabulário e testes da 024 afetados

Testes da 024 que mudam, com rastreabilidade (025 "Requisitos revisados"):

| Teste | Mudança |
|---|---|
| `VEDADOS` de `test_inicio.py` | "Oportunidade" passa a ser vetada **fora** do bloco |
| `test_pesquisa_so_no_convite` | Passa a ignorar o bloco de Oportunidades. Um título pode conter "pesquisa" ("Pesquisa e extensão"); o FR-022 da 025 trata isso. O convite continua sendo a única chamada à pesquisa de acompanhamento |
| `test_navegacao_nas_telas_fora_das_secoes` | Cinco itens; a página `/oportunidades/` também tem navegação |
| `test_portal_sem_modelo_nem_migracao` | Ver R1 |
| `test_portal_nao_grava` | Acrescenta `/oportunidades/` às telas que não gravam |

## R12 — Privacidade do link

**Decisão.**
- Link direto, na mesma aba, com `rel="noreferrer"`: o site externo não recebe a página de
  origem.
- Nenhum parâmetro é acrescentado ao endereço.
- Nenhuma visualização ou clique é registrado (FR-015).
- Logs: o padrão do Django (método, caminho, status), sem a Pessoa.

## R13 — Exclusão do dado analítico

**Decisão.** A exclusão é garantida por construção: as listas de importação permitidas de
`analitico` e `exportacao` não incluem o `portal`, e um teste confirma.

**Teste novo.** Snapshot e exportações gerados antes e depois de publicar oportunidades são
idênticos (025 SC-009).

## R14 — Textos

**Decisão.** Os textos ficam em `portal/oportunidades/mensagens.py` e são provisórios
(008/DP-801). Os textos finais estão em
[contracts/oportunidades-egresso.md](contracts/oportunidades-egresso.md) e
[contracts/curadoria.md](contracts/curadoria.md). Vocabulário vetado:
- "recomendado";
- "não perca";
- "últimas vagas";
- "selecionado para você";
- contagens de outros egressos;
- estimativas de tempo.
