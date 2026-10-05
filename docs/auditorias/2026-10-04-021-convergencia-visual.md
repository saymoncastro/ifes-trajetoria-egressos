# Auditoria de convergência visual e narrativa — Feature 021

Data: 2026-10-04. Base: branch `claude/academic-data-structure-c7318c`, PR #30 aberto, com
P1 e P2 implementadas.

**O que esta auditoria faz e não faz**

- **Só diagnostica e propõe.** Não altera domínio, não acrescenta dado e não muda o
  renderer.
- **A P2 já estava implementada** quando a pausa foi pedida (`contexto_trajetoria`,
  ingresso e agregados). Esta auditoria não mexe nela.
- **O que muda depois é só a apresentação dos mesmos dados.** No card, as contagens viram
  destaques. A camada de domínio e a montagem não mudam.
- **O protótipo é um esboço descartável.** Os PNGs `proto-*` vêm de um script avulso
  ([prototipo_card.py](evidencias-021-visual/prototipo_card.py)), fora do renderer. Usam
  dados fictícios e uma ilustração vetorial fictícia.

**Material comparado**

1. **Mockup de referência:** 12 telas e o card.
   [mockup-referencia.webp](evidencias-021-visual/mockup-referencia.webp)
2. **PNGs atuais:**
   [atual-card-maria.png](evidencias-021-visual/atual-card-maria.png),
   [atual-card-ana-p2.png](evidencias-021-visual/atual-card-ana-p2.png),
   [atual-card-pior-caso.png](evidencias-021-visual/atual-card-pior-caso.png).
3. **Página atual:**
   [pagina-375-ana-p2.jpg](../../specs/021-minha-trajetoria-narrativa/evidencias/pagina-375-ana-p2.jpg).
4. **Artefatos da 021:** spec, plan, contratos e tasks.

---

## 1. Diagnóstico: distância entre o atual e o mockup

O resultado atual é **correto e legível, mas é um relatório textual diagramado em 1080 ×
1920**. O mockup é uma **peça editorial**, com direção de arte, ritmo e pertencimento. A
distância não se resolve com acabamento.

| Camada | Atual | Mockup | Efeito |
|---|---|---|---|
| Composição | Texto empilhado de cima para baixo; rodapé ancorado embaixo | Zonas com função: marca, título, imagem, linha do tempo, destaque, fecho | Sem leitura em três segundos |
| Elemento visual dominante | Nenhum (só faixas pretas e fio verde) | Fotografia ou elemento institucional forte | A peça não "parece Ifes" nem parece social |
| Formações | Blocos de texto (curso em negrito + atributos) | **Linha do tempo**: ano em destaque, nó, traço | Não comunica trajetória |
| Agregados | Parágrafo de 3 a 5 linhas | Número grande + rótulo curto, em cartão | O dado mais "compartilhável" vira letra miúda |
| Proveniência | "Dados institucionais apurados em…" no corpo | Rodapé discreto | Compete com a história |
| Uso do quadro | ~600 px de conteúdo e ~800 px vazios (Maria, Ana) | Quadro ocupado de propósito | A peça parece inacabada |
| Hierarquia tipográfica | 3 tamanhos próximos (64/44/40) | Contraste forte: título, ano, curso, número | Tudo com o mesmo peso |
| Identidade | Só o nome em texto no rodapé | Assinatura, verde institucional, cartões, ícones | Sem pertencimento |
| Emoção e ritmo | Nenhum fecho | Começo, continuidade, pertencimento ("Essa história também é minha.") | Sem motivo para compartilhar |
| Página web | Seções de texto com fio verde | Capítulos visuais com imagem, ícones e progresso | A experiência não é uma devolutiva |

**O que está certo e fica:**

- o pipeline `TrajetoriaNarrativa → SVG → PNG`, que é determinístico e reprodutível;
- a área segura;
- as fronteiras de domínio;
- a precisão semântica;
- a composição adaptativa;
- o nome opcional.

O erro foi de **especificação da camada de apresentação**, não de arquitetura.

---

## 2. Causas na spec, no plan e nas tasks

1. **A spec traduziu a visão em correção de dados, sem ambição visual.** A frase "gerar
   uma representação determinística em SVG/PNG" virou o objetivo. Não havia critério de
   aceitação visual: o SC-013 mede tamanho e área segura, não comunicação.
2. **Proibições defensivas tiraram o elemento dominante.**
   - **FR-029:** "sem fotos".
   - **DP-2106:** nenhuma imagem.
   - **FR-036 e DP-2102:** card sem marca gráfica.

   Cada uma tinha razão (direito de uso, falsa memória, decisão da ACS), mas somadas
   deixaram o card sem nenhum elemento além de texto.
3. **O tema do card foi derivado dos tokens da 015 (FR-040)**, que são a identidade de um
   *formulário sóbrio*, não de uma peça social.
4. **O catálogo foi desenhado para frases de página e o card reaproveitou as frases
   inteiras.** O FR-061 só admitia as formulações completas, e a precisão virou parágrafo.
5. **O motor de layout empilha de cima para baixo.** O `card.compor` não tem regra de
   ocupação do quadro: o rodapé ancorado embaixo cria o vazio no meio.
6. **Contratos e tasks testaram o "cabe", não o "comunica".** O `card.md` define conteúdo
   permitido, não composição. A porta da Fase 3 validou "o pior caso cabe com 40 px". Os
   testes medem área segura e corpo mínimo, não hierarquia nem ocupação.
7. **A página reaproveitou o estilo da jornada da pesquisa** (seções de texto). Os
   capítulos do mockup foram lidos como "seções que somem sem dado", sem componente visual
   nenhum.

---

## 3. Design system narrativo mínimo

Os componentes são **funções de composição** no `narrativa/card.py` (SVG) e **includes** no
template da página. Não há framework, motor de temas nem configuração. Cada componente
recebe só valores já prontos da `TrajetoriaNarrativa`.

| Componente | Card (SVG) | Página (HTML) | Dados |
|---|---|---|---|
| `Marca` | Assinatura sobre pílula clara no topo da área segura (**decisão V1**) | Já existe no cabeçalho | — |
| `Abertura` (imagem institucional) | Ilustração ou fotografia em sangria total, de y = 0 até a borda em onda; **absorve o espaço livre** do quadro; legenda honesta "Unidade X · ilustração" (**decisão V2**) | Faixa de abertura no topo da página, com a mesma imagem | unidade da primeira formação exibida |
| `Titulo` | "Minha trajetória" (verde profundo) / "no Ifes" (verde marca), 84 px negrito; nome opcional em 44 px | `h1` com a mesma hierarquia | nome (FR-034) |
| `LinhaDoTempo` + `No` | Traço vertical e nós circulares; **ano em 44 px verde negrito**, curso em 44 px negrito, atributos em 36 px | `ol` com marcadores em CSS (nó, traço, ano em destaque) | formações, ano, relação "depois" |
| `Destaque` (estatística) | Cartão branco com filete verde: **número de 88 a 96 px** e rótulo de 2 linhas (30 px) | Cartão com número grande + frase completa em letra menor | contexto agregado (P2) |
| `Fecho` | "Essa história também é minha." em 46 px (**decisão V3**) | Mesma frase antes do card | — (texto fixo do catálogo) |
| `Rodape` | Instituição, demonstração e proveniência em 26–28 px, ancorados na base da área segura | Proveniência junto do destaque | apuração |
| `FaixaInferior` | Verde profundo com grafismo (sob a interface do story, sem texto) | — | — |

**Paleta própria do card**, derivada da marca, com contraste AA verificado por teste:

| Token | Valor |
|---|---|
| verde profundo | `#0e3b23` |
| verde marca | `#2f9e41`, só em grafismo e no "no Ifes" de corpo grande |
| creme | `#f6f2e8` |
| branco dos cartões | `#ffffff` |
| texto | `#1b1b1b` |
| texto suave | `#4a5058` |

Os hex de ação da 015 continuam vetados no código.

**Ícones:** não são necessários no card (a linha do tempo e os números fazem o papel). Na
página, ícones simples desenhados à mão, sem biblioteca, podem acompanhar os capítulos.

**Tipografia:** continua só com Open Sans Regular e Bold. Sem fonte manuscrita: o fecho em
negrito cumpre o papel sem novo arquivo de fonte.

---

## 4. Wireframe estrutural do novo card

Protótipos: [proto-maria-2-formacoes-agregados.png](evidencias-021-visual/proto-maria-2-formacoes-agregados.png) ·
[proto-ana-1-formacao-agregados-sem-marca.png](evidencias-021-visual/proto-ana-1-formacao-agregados-sem-marca.png) ·
[proto-diego-3-formacoes-sem-agregados.png](evidencias-021-visual/proto-diego-3-formacoes-sem-agregados.png) ·
[proto-pior-caso-4-formacoes-e-mais.png](evidencias-021-visual/proto-pior-caso-4-formacoes-e-mais.png)

```text
y=0     ┌──────────── ABERTURA (imagem institucional, sangria) ───────────┐
        │  (sob a interface do story: só imagem)                        │
y=270   │  [Marca]                                                      │  ← área segura
        │                                   [Unidade Serra · ilustração]│
y≈hero  └──────────────── borda em onda ────────────────────────────────┘
        TÍTULO   Minha trajetória
                 no Ifes
                 Nome (opcional)
        LINHA    ● 2022  Tecnologia em Análise e Desenvolvimento…
        DO       │       Serra · Graduação · Presencial
        TEMPO    ● 2025  Especialização em Informática na Educação
                         Cefor · Pós-graduação · A distância
                 [e mais N formações registradas]
        DESTAQUE ┌─────────────┐ ┌─────────────┐
                 │ 27          │ │ 812         │
                 │ conclusões  │ │ conclusões  │
                 │ deste curso…│ │ registradas…│
                 └─────────────┘ └─────────────┘
        FECHO    Essa história também é minha.
y=1650  RODAPÉ   Instituto Federal do Espírito Santo · Demonstração — dados fictícios
                 Dados institucionais apurados em 31/01/2026.
        ┌──────────── FAIXA INFERIOR (grafismo, sem texto) ───────────────┐
y=1920  └─────────────────────────────────────────────────────────────────┘
```

**Regra central de ocupação: a abertura absorve o espaço livre.**

- A altura da imagem é a área segura menos o conteúdo medido, entre um mínimo e um
  máximo.
- Com pouco conteúdo, a imagem cresce (Ana). Com muito, ela vira uma faixa (pior caso).
- **Não sobra vazio no meio:** o fecho e o rodapé ficam na base, e o conteúdo se acomoda
  logo abaixo da imagem.

**Área segura revista:** y de 270 a 1650, alinhada à orientação da Meta para stories (cerca
de 14% livres no topo e na base). O valor anterior, 1570, era mais conservador que o
necessário. O plan fixa o número.

---

## 5. Tratamento dos diferentes volumes de conteúdo

| Caso | Abertura | Linha do tempo | Destaques | Observação |
|---|---|---|---|---|
| 1 formação, sem agregados | Grande (até o máximo) | 1 nó, sem traço | — | Título e fecho ganham respiro |
| 1 formação + agregados (Ana) | Média | 1 nó | 2 cartões | Ver protótipo |
| 2 formações + agregados (Maria) | Faixa média | 2 nós com traço | 2 cartões, só se couberem | Ver protótipo |
| 3–4 formações, sem agregados (Diego) | Faixa | 3–4 nós | — | Ver protótipo |
| Mais de 4, ou textos muito longos | Faixa mínima | Até 4, tantas quantas couberem, + "e mais N" | Saem primeiro | Composição adaptativa aprovada; nome e cursos nunca cortados |
| Sem imagem da unidade | Imagem genérica do Ifes, legenda "Ifes · ilustração" | — | — | Nunca fica sem elemento dominante |
| Sem nome (ou não escolhido) | — | — | — | O título sobe |
| Só um agregado selecionado | — | — | 1 cartão em largura total | — |

**Ordem de corte no card:**

1. Encolher a abertura até o mínimo.
2. Retirar os destaques.
3. Converter formações em "e mais N".

Na página, nada é cortado: ela mostra tudo.

---

## 6. Revisão da página (story web)

**Proposta:** uma página única em **capítulos visuais**, sem JavaScript obrigatório e sem
rota nova.

```text
ABERTURA     imagem institucional + "Minha trajetória no Ifes" + nome (se houver)
             "O Ifes registra N formações concluídas por você."
CAPÍTULO 1   "Sua formação"                     (sempre)
             [P2] "Sua trajetória no Ifes começou em AAAA…" (se ingresso)
             nó da primeira formação: ano grande, curso, atributos, "Há N anos…"
CAPÍTULO 2   "Sua continuidade no Ifes"         (só com 2 ou mais formações)
             linha do tempo das demais formações + frases "Depois dessa formação…"
CAPÍTULO 3   "Naquele ano no Ifes"              (só com agregado selecionado)
             cartões com número grande + frase completa e precisa + apuração
SEU CARD     prévia PNG + nome + Baixar + Compartilhar (como hoje)
```

- **Indicador de capítulo** ("Capítulo 1 de 3"): calculado pelos capítulos presentes.
  Some quando há um só.
- Cada capítulo é um bloco de largura total, com fundo alternado (creme e branco) e o mesmo
  vocabulário visual do card (nó, traço, cartão). O ritmo vem da composição, não de telas
  separadas.
- **A tela "Preparando sua trajetória" fica fora.** Não há processamento a esperar, e uma
  espera artificial seria encenação. A emoção da transição migra para a abertura.
- **Confirmação da pesquisa:** pode ganhar estilo de botão na ação única "Ver minha
  trajetória no Ifes". A 014 FR-041 continua: uma ação só.

---

## 7. Matriz: elemento do mockup × intenção × situação × decisão

| Elemento do mockup | Intenção de produto | Existe hoje? | Decisão | Implementação proposta |
|---|---|---|---|---|
| 1. Convite "Olá, X! O Ifes guarda uma parte da sua história" + foto | Acolher e prometer devolutiva | Parcial (antecipação em texto, FR-070) | Adaptar depois | Fora da 021; candidata a ajuste da tela de formações numa feature de jornada |
| 2. "O que já sabemos" (lista com ícones) | Mostrar o que o Ifes sabe | Sim (texto) | Adaptar | Abertura com "O Ifes registra N formações" + linha do tempo; ícones na página |
| 3. Formulário "como está sua trajetória hoje" | Coletar declarado | Não (é a pesquisa) | Manter fora | É o instrumento (008); a 021 não lê Respostas |
| 4. "Preparando seu retrato" (transição) | Emoção, expectativa | Não | **Adiar / descartar** | Sem espera artificial; a emoção vai para a abertura |
| 5. "Foi aqui que tudo começou — 2005" + polaroide "Campus Vitória · 2005" | Início da história | Parcial (frase de início com ingresso, P2) | Adaptar | Frase só com ingresso real; imagem **sem ano** e com legenda "ilustração"; nunca "foto da época" |
| 5. "Naquele ano… 1.240 estudantes matriculados" | Contexto do período | Não | **Vetado** | Sem métrica de matriculados (FR-024); só as duas contagens de conclusões |
| 6. "Momentos que fizeram parte da sua história" (projetos) | Marcos | Não (P3) | Adiar | Lista de marcos já prevista na narrativa; sem fonte, não aparece |
| 7. "Além do técnico, você continuou no Ifes" | Continuidade | Sim (frase "depois") | Manter e realçar | Capítulo 2 com linha do tempo |
| 7. "Poucos egressos seguem com mais de uma formação" | Pertencimento por comparação | Não | **Vetado** | Comparação sem dado; fora |
| 8. "E hoje, onde você está?" | Situação atual | Não | Manter fora | Dado declarado (DP-2107) |
| 9. "Você faz parte de uma grande geração" + percentuais | Pertencimento coletivo | Não | **Vetado** | "Geração", "turma" e percentuais vedados (FR-024, FR-061) |
| 10. Card: marca no topo | Identidade | Não | **Decisão V1** | Assinatura na demonstração |
| 10. Card: título "Minha trajetória no Ifes" | Nome da peça | Sim | Manter, com hierarquia forte | `Titulo` |
| 10. Card: linha do tempo 2005 → 2008 → 2011 | Trajetória | Não (texto) | **Adaptar (central)** | `LinhaDoTempo`; ingresso só quando existir |
| 10. Card: foto pessoal do egresso | Personalização | Não | Manter fora | Sem upload (FR-041) |
| 10. Card: "#SouEgressoIfes" | Campanha, alcance | Não | Adiar | Depende da ACS (nova DP-2110) |
| 10. Card: "Essa história também é minha." | Pertencimento, fecho | Não | **Decisão V3** | `Fecho`, texto fixo do catálogo |
| 10. Card: vegetação, fotografia, textura | Atmosfera institucional | Não | **Decisão V2** | `Abertura` com ilustração vetorial ou fotografia licenciada |
| 11. Estilos de card (vários temas) | Escolha e expressão | Não | Adiar (P3) | O template já recebe `tema` |
| 12. "Obrigado…" + atalhos do Portal | Encerramento e relação contínua | Parcial (confirmação) | Manter fora | Portal é DP-2108 |

---

## 8. Alterações necessárias (a aplicar depois das decisões V1 a V3)

**Spec**
- E6 e uma seção nova, "Direção visual": o card é peça editorial e a página é uma
  experiência em capítulos.
- FR-029 revisado: imagem institucional decorativa permitida por catálogo com metadados
  (unidade, origem, licença, "ilustração/fotografia"), nunca afirmando período.
- FR-036 revisado conforme V1.
- FR-040 revisado: tema próprio do card derivado da marca, com AA.
- FR-061 ampliado: no card, as contagens aparecem decompostas em número + rótulo, com a
  mesma semântica. A frase completa fica na página.
- **FRs novos:**
  - componentes;
  - ocupação do quadro (a abertura absorve o livre);
  - linha do tempo;
  - destaques;
  - fecho;
  - proveniência no rodapé;
  - capítulos da página;
  - legenda honesta da imagem.
- SC-015 com os critérios visuais da §9; SC-013 com a área segura revista.
- **Decisões pendentes:** DP-2102 e DP-2106 atualizadas; nova DP-2110 (hashtag e assinatura
  de campanha, com a ACS).
- **Status:** "P1 visual reaberta".

**Plan e research**
- R10 revisado: área segura de 270 a 1650; corpo mínimo de 40 px no conteúdo e de 26 px no
  rodapé e na proveniência.
- R19, componentes e motor de zonas com preenchimento.
- R20, catálogo de imagens: arquivos no app com metadados; ilustração genérica de
  fallback; fotografia só com licença registrada.
- R21, capítulos da página.
- Complexity Tracking: ativos de imagem.

**Contratos**
- `card.md` reescrito como composição (zonas, componentes, regras de corte).
- `catalogo.md` com as formulações do card (`destaque_curso`, `destaque_unidade`, `fecho`,
  legenda).
- `rotas.md` com a estrutura em capítulos.
- Novo `imagens.md` (catálogo e metadados), ou uma seção no `card.md`.

**Tasks:** uma fase nova, "Convergência visual", entra antes de qualquer outra mudança de
P2.
- **Testes de critério visual:** ocupação, hierarquia, nós por formação, nenhuma métrica
  em parágrafo, legenda da imagem.
- **Implementação:** componentes do card, catálogo de imagens, ilustração de fallback,
  página em capítulos.
- **Revisão:** conjunto de PNGs de referência por caso, revisado pelo solicitante.

As tasks visuais anteriores (T008 a T012, T028 e T029) ficam como "superadas na
composição". O pipeline e os testes de área segura continuam.

---

## 9. O que continua fora da 021

- Foto pessoal e upload.
- Fotografia histórica atribuída ao período do egresso.
- "Geração", "turma", "matriculados", percentuais e comparações.
- Dados declarados ("Hoje").
- Marcos e projetos (P3, sem fonte).
- Vários temas de card (P3).
- Hashtag de campanha (até a ACS).
- Tela de espera artificial.
- Atalhos do Portal.
- Vídeo (022).
- IA generativa para conteúdo ou imagem.

---

## 10. Critérios objetivos de aceitação visual

Ver SC-015. São verificados por teste quando o critério é mensurável, e por revisão do
solicitante sobre um conjunto fixo de PNGs de referência.

1. **Elemento visual dominante:** o card tem um elemento visual não textual que ocupa pelo
   menos 20% da área do quadro, em todos os casos de referência.
2. **Trajetória:** cada formação exibida tem um nó gráfico com ano em destaque (quando
   houver ano). Com duas ou mais, há traço ligando os nós.
3. **Nenhuma métrica em parágrafo:** cada contagem no card tem número de pelo menos 80 px e
   rótulo de no máximo 2 linhas. A frase completa existe só na página.
4. **Ocupação:** dentro da área segura não há faixa vazia contínua maior que 160 px, nos
   casos de 1 a 4 formações, com e sem agregados.
5. **Hierarquia:** pelo menos quatro níveis tipográficos distintos (título ≥ 80 px;
   ano/número ≥ 44 px; curso ≥ 40 px; rodapé ≤ 30 px). A proveniência fica só no rodapé.
6. **Legibilidade no story:** conteúdo com corpo ≥ 40 px, rodapé ≥ 26 px, contraste AA,
   todo texto na área segura.
7. **Robustez:**
   - 1, 2, 3, 4 e mais de 4 formações;
   - com e sem agregados;
   - com e sem imagem da unidade;
   - com e sem nome.

   Em todos os casos, nada sobreposto, nada cortado e "e mais N" quando preciso.
8. **Honestidade:** a imagem tem legenda visível "Unidade X · ilustração" (ou "fotografia"),
   nunca com ano. Nenhuma frase fora do catálogo. Nenhum termo vedado.
9. **Revisão do solicitante:** o conjunto de PNGs de referência
   (`specs/021-…/evidencias/referencia-*.png`) é aprovado antes do merge.

---

## 11. Decisões do solicitante necessárias

- **V1 — Marca no card, na demonstração.** Recomendado: usar a assinatura oficial que o
  sistema já exibe no cabeçalho, com DP-2102 aberta para produção (ACS).
  - Alternativa: só o nome em texto. O protótipo da Ana mostra essa opção, e ela enfraquece
    a identidade.
- **V2 — Origem das imagens.** Recomendado: ilustração vetorial própria e genérica (sem
  licença de terceiros, sem afirmar lugar real), com legenda "Unidade X · ilustração". O
  catálogo por unidade fica pronto para fotografias licenciadas quando a ACS fornecer
  (DP-2106).
  - Alternativa A: fotografias de uso livre (por exemplo, Wikimedia Commons, CC BY-SA), com
    atribuição visível. Exige cuidado de licença e crédito no card.
  - Alternativa B: esperar as fotos da ACS. O card fica sem elemento dominante até lá.
- **V3 — Frase de fecho.** Recomendado: "Essa história também é minha." como texto fixo do
  catálogo (hipótese de produto, revisável). A hashtag fica fora até a ACS.

### Decisões do solicitante (2026-10-05)

| Decisão | Escolha | Observação |
|---|---|---|
| V1 | Assinatura oficial no card de demonstração | DP-2102 aberta para produção |
| V2 | Ilustração vetorial própria e genérica, legenda "Unidade X · ilustração" | Catálogo pronto para fotografias licenciadas (DP-2106) |
| V3 | "Essa história também é minha." **com** `#SouEgressoIfes` | Hipótese de produto; nova DP-2110 para produção |
| PR #30 | Convertido em rascunho até a aprovação do novo visual | — |

As alterações da §8 foram aplicadas na spec, no plan, no research, nos contratos e nas
tasks (Fase 13, T056 a T065). O renderer não foi alterado.
