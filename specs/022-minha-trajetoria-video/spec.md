# Feature Specification: Minha Trajetória em vídeo

**Feature**: `022-minha-trajetoria-video`

**Feature Branch**: `claude/trajetoria-video-remotion-2faa72` (a partir da `main` em
`a65d7cb`, com a 021 mergeada pelo PR #30)

**Created**: 2026-10-05

**Status**: Draft

**Input**: Solicitação da Feature 022 — Minha Trajetória em vídeo com Remotion.

- O egresso obtém um vídeo vertical curto, sem áudio e compartilhável, da "Minha trajetória
  no Ifes", produzido a partir da mesma `TrajetoriaNarrativa` da Feature 021.
- O vídeo funciona como micro-retrospectiva de cerca de 8 segundos, não como apresentação
  institucional.
- Mesma entrada e mesma versão do template dão o mesmo conteúdo audiovisual.
- O vídeo não usa IA generativa e não inventa textos, acontecimentos, imagens, datas nem
  relações acadêmicas.
- O vídeo é derivado opcional: sua falha não afeta nada da 021.

## Contexto

A [auditoria da 022](../../docs/auditorias/2026-10-05-022-video-trajetoria.md) mostrou que
o storyboard pedido percorre exatamente as zonas do card editorial da 021, na mesma ordem:

1. abertura;
2. título;
3. linha do tempo;
4. destaques;
5. fecho e rodapé.

O card já é composto por zonas posicionadas, com quebras de linha medidas e as regras de
corte e ocupação da 021 (FR-080, FR-082). O vídeo, portanto, é **o card ganhando
movimento**: cada zona entra no seu instante e o quadro final é o card.

```text
TrajetoriaNarrativa (021, inalterada)
        │
        ▼
composição visual do card, agrupada por zonas (ComposicaoVisual)
 ├─ abertura (imagem da unidade, marca, legenda)
 ├─ título (e nome, por escolha)
 ├─ linha do tempo
 ├─ destaques
 ├─ fechamento
 └─ rodapé
        │
        ├──► PNG 1080 × 1920 (021)
        └──► MP4 1080 × 1920 (022: um único template anima as zonas; não refaz layout)
```

### Base existente e evidências

- **Contrato da narrativa (021, versão 1):**
  - `TrajetoriaNarrativa` é pura, determinística, serializável e não persistida.
  - O subconjunto `compartilhavel` já aplica as regras do card: formações exibidas, "e mais
    N", destaques e apuração.
  - O nome é acrescentado pela rota, por escolha (021 FR-034).
- **Composição do card (021):**
  - Elementos SVG posicionados, cada um com a classe da sua zona.
  - Hoje é uma lista plana. Agrupá-la por zona é mudança interna, sem efeito no SVG.
- **Ativos:**
  - Open Sans (OFL);
  - ilustração genérica própria;
  - assinatura do Ifes;
  - todos versionados no repositório.
- **Infraestrutura:**
  - Não há fila, worker, armazenamento de mídia nem ambiente de produção.
  - Tudo roda em modo de demonstração.
- **Spike da auditoria (alternativa C, fora do repositório):**
  - As zonas reais do card foram animadas e rasterizadas pelo `resvg` da 021.
  - Os quadros saíram corretos, a cerca de 106 ms por quadro.
  - O resultado prova que a composição por zonas basta como entrada.

### Escolhas desta spec (decisões do solicitante, 2026-10-05)

- **E1 — O motor anima a composição da 021 (alternativa A).**
  - Um único template de vídeo, construído com Remotion, recebe a composição serializada.
  - Ele só anima as zonas. Não refaz layout, não mede texto, não aplica regra de dado e
    não gera frase.
- **E2 — Sem segundo layout (alternativa B descartada).**
  - Não há reimplementação da composição em outra tecnologia.
- **E3 — O caminho Python (alternativa C) fica só como spike e fallback técnico
  documentado.**
  - Não é a arquitetura da 022 nem motor de animação próprio.
- **E4 — Execução não fixada nesta spec.**
  - O research/plan compara duas soluções mínimas, a partir de um spike do motor:
    - **geração síncrona**, se o tempo for previsível e aceitável numa requisição;
    - **estado técnico mínimo persistido** (solicitado → processando → pronto ou falhou),
      com processamento fora da requisição.
  - Ficam vedados: fila em sistema de arquivos, broker de mensagens e entidade de domínio
    de vídeo.
  - **Resolvido no plan** ([research](research.md) R0 e R5): **assíncrono com estado
    técnico mínimo**. O tempo de render medido varia de 3 a 9 s numa máquina rápida e
    depende do hardware.
- **E5 — Cache técnico aceito.**
  - A chave combina a composição e a versão do template.
  - A retenção é curta.
  - O cache é otimização e não vira histórico.
- **E6 — Licença.**
  - A documentação atual do Remotion declara organizações *non-profit/not-for-profit*
    elegíveis à licença gratuita.
  - O Remotion é *source-available*, não open source no sentido OSI.
  - O aceite institucional da licença, dos termos e de eventuais licenças de codec fica
    como decisão pré-produção (DP-2201).
  - A licença não bloqueia esta spec nem a demonstração.
- **E7 — Números estáticos.**
  - Os destaques aparecem com o valor final, sem contagem animada.
  - A contagem não agrega e aumenta o ruído.

### Storyboard-base (alvo de 8 s)

| Tempo | Zona da composição | Movimento |
|---|---|---|
| 0,0–0,7 s | Abertura: imagem da unidade, marca, legenda | Imagem com leve aproximação e opacidade; marca e legenda entram |
| 0,7–1,7 s | Título "Minha trajetória no Ifes" e nome, se escolhido | Entrada com opacidade e pequena translação |
| 1,7–5,0 s | Linha do tempo | O traço se desenha de cima para baixo; cada formação (ano, curso, unidade · nível · modalidade) entra em sequência; "e mais N" por último |
| 5,0–6,3 s | Destaques, se houver | Cartões entram com números estáticos |
| 6,3–8,0 s | Fechamento | "Essa história também é minha." e `#SouEgressoIfes` entram; a composição converge para o card. Nos últimos 1–1,3 s quase nada se move |

O rodapé ("Instituto Federal do Espírito Santo · Demonstração — dados fictícios") fica
visível do primeiro ao último quadro.

## Clarifications

### Session 2026-10-05 (auditoria da 022 e revisão do solicitante)

- Q: Qual motor de renderização? → A: **A, Remotion animando a composição da 021**. B (layout
  próprio em React) descartada. C (Python/resvg) mantida só como spike e fallback.
- Q: A entrada do vídeo é o JSON da `TrajetoriaNarrativa`? → A: Não basta. Faltam os textos
  prontos, o nome e as decisões de layout. A entrada é a **composição visual do card**,
  projeção mecânica agrupada por zona, sem modelo semântico novo.
- Q: Pasta de pedidos como fila? → A: **Não.** O plan compara geração síncrona com um
  estado técnico mínimo persistido. Uma tabela técnica com migration é aceitável se o
  assíncrono for necessário.
- Q: Contador nos números agregados? → A: Não. Números estáticos.
- Q: Timing → A: o do storyboard acima. Duração máxima de 10 s, só para legibilidade.
- Q: A licença bloqueia? → A: Não bloqueia a spec nem a demonstração. Vira decisão
  institucional pré-produção.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gerar e baixar o vídeo da própria trajetória (Priority: P1)

Na página "Minha trajetória no Ifes", o egresso vê o card e, ao lado dele, a opção de gerar
um vídeo curto da trajetória. Ele pede o vídeo, acompanha um aviso de preparação quando a
geração não é instantânea e, com o vídeo pronto, assiste a uma prévia, baixa o arquivo ou
usa o compartilhamento do próprio celular.

**Why this priority**: É o valor da feature, uma versão em movimento do card, pronta para o
story.

**Independent Test**: Com uma Pessoa fictícia elegível, abrir a página, pedir o vídeo e
obter um MP4 vertical de cerca de 8 s que reproduz no celular.

**Acceptance Scenarios**:

1. **Given** uma Pessoa elegível na página da trajetória, **When** ela pede o vídeo,
   **Then** recebe, de imediato ou depois do aviso "Estamos preparando seu vídeo…", um
   vídeo vertical 1080 × 1920, sem áudio, com duração entre 7 e 10 s.
2. **Given** o vídeo pronto, **When** a Pessoa escolhe baixar, **Then** o arquivo chega com
   o nome neutro `minha-trajetoria-ifes.mp4`.
3. **Given** um navegador que compartilha arquivos, **When** a Pessoa escolhe compartilhar,
   **Then** abre-se o menu de compartilhamento do sistema com o vídeo. Nenhum resultado
   depende de um aplicativo específico aparecer no menu.
4. **Given** um navegador que não compartilha arquivos, **When** a página é exibida,
   **Then** o botão de compartilhar não aparece e baixar continua disponível.
5. **Given** a Pessoa abre a página, **When** ela ainda não pediu o vídeo, **Then** nenhum
   vídeo é gerado automaticamente.

---

### User Story 2 - O vídeo é o card em movimento (Priority: P1)

O egresso reconhece no vídeo exatamente o card que já viu: a mesma ilustração, as mesmas
cores, a mesma tipografia, a mesma linha do tempo e os mesmos destaques. Ao final, o vídeo
para no próprio card, tempo suficiente para a leitura.

**Why this priority**: A 022 não cria outra identidade visual. O vídeo e o PNG são duas
renderizações do mesmo produto visual.

**Independent Test**: Para cada caso de referência, comparar o quadro final do vídeo com o
PNG do card da mesma escolha de nome, e comparar o conjunto de textos do vídeo com o do
card.

**Acceptance Scenarios**:

1. **Given** um caso de referência, **When** o vídeo é gerado, **Then** o quadro final
   coincide com o card PNG da mesma escolha de nome, dentro da tolerância definida no plan.
2. **Given** qualquer caso, **When** o vídeo é gerado, **Then** todo texto que aparece no
   vídeo também aparece no card, e todo texto do card aparece no vídeo.
3. **Given** o vídeo, **When** observado no último 1 s, **Then** a imagem fica estável, sem
   movimento perceptível.
4. **Given** uma composição com destaques, **When** os destaques entram, **Then** os números
   aparecem já com o valor final, sem contagem.

---

### User Story 3 - Vídeo correto em todos os casos (Priority: P1)

Seja qual for a trajetória (uma ou várias formações, cursos de nome longo, com ou sem
agregados, com ou sem nome, sem imagem própria da unidade), o vídeo mostra o mesmo conteúdo
do card, sem texto cortado, sobreposto ou fora da área segura, sem bloco vazio e sem zero
inventado.

**Why this priority**: Um vídeo errado em um caso real compromete a confiança na
devolutiva inteira.

**Independent Test**: Gerar os vídeos da matriz de casos extremos e verificar automaticamente
textos, posições nos quadros-chave e duração.

**Acceptance Scenarios**:

1. **Given** 1, 2, 3 ou 4 formações exibidas, **When** o vídeo é gerado, **Then** cada
   formação entra como um nó, na ordem do card, e a duração fica entre 7 e 10 s.
2. **Given** mais formações do que o card exibe, **When** o vídeo é gerado, **Then** ele
   mostra as mesmas formações do card e a mesma linha "e mais N formações registradas".
3. **Given** uma composição sem destaques, **When** o vídeo é gerado, **Then** não há bloco
   de destaques, nenhum número aparece e o tempo correspondente vira permanência do quadro
   final.
4. **Given** um ou dois destaques no card, **When** o vídeo é gerado, **Then** aparecem os
   mesmos destaques, com o mesmo número e o mesmo rótulo.
5. **Given** nome não escolhido, ou indisponível, **When** o vídeo é gerado, **Then**
   nenhum nome aparece em quadro algum.
6. **Given** uma unidade sem imagem própria, **When** o vídeo é gerado, **Then** aparece a
   ilustração genérica com a legenda "· ilustração", e nada afirma retratar o período do
   egresso.
7. **Given** nomes de curso ou unidade longos e com acentos, **When** o vídeo é gerado,
   **Then** as quebras de linha são as do card e nenhum texto sai da área segura em nenhum
   quadro-chave.
8. **Given** uma composição que o card não consegue representar nem no mínimo, **When** o
   vídeo é pedido, **Then** a geração falha explicitamente, sem cortar informação em
   silêncio.

---

### User Story 4 - Espera e falha não atrapalham (Priority: P1)

Se a geração demora ou falha, o egresso continua usando a página: lê a trajetória, baixa o
PNG e volta às formações. A falha aparece como mensagem compreensível, com a opção de
tentar de novo, e nada do que ele já fez muda.

**Why this priority**: O vídeo é derivado opcional. Não pode se tornar um ponto de falha da
devolutiva.

**Independent Test**: Simular renderizador indisponível, falha de geração e geração lenta.
Verificar a página, o card e a contagem de Participações e Respostas antes e depois.

**Acceptance Scenarios**:

1. **Given** uma geração em andamento, **When** a Pessoa recarrega ou volta à página,
   **Then** vê "Estamos preparando seu vídeo…" e todo o restante da página funciona.
2. **Given** uma geração que falhou, **When** a Pessoa volta à página, **Then** vê uma
   mensagem compreensível e a opção de tentar novamente. O card PNG continua disponível.
3. **Given** um ambiente sem o renderizador de vídeo, **When** a página é aberta, **Then**
   a opção de vídeo não aparece (ou aparece como indisponível) e a página e o card
   funcionam normalmente.
4. **Given** qualquer resultado da geração (pronto, falha ou indisponível), **When**
   comparado ao estado anterior, **Then** Participação, Respostas, narrativa e card são
   idênticos.
5. **Given** pedidos repetidos da mesma Pessoa para o mesmo conteúdo, **When** um já está em
   andamento ou pronto, **Then** nenhuma geração duplicada é iniciada.

---

### Edge Cases

- **Uma formação:** sem traço entre nós; o nó único ocupa a janela da linha do tempo.
- **Quatro formações:** a linha do tempo ganha 0,6 s (vídeo de 8,6 s) e cada nó fica com
  cerca de 1 s. As janelas seguintes se deslocam pelo mesmo acréscimo (FR-011). Nunca
  passa de 10 s.
- **Mais de quatro formações:** vale a regra do card (até 4 exibidas e "e mais N"). O vídeo
  não muda os dados para caber.
- **Curso ou unidade longos:** as quebras são as do card; o vídeo não remede texto.
- **Sem agregado / um agregado / dois agregados:** destaques ausentes, um cartão ou o par,
  conforme o card. Sem agregado, não há bloco nem zero.
- **Duas apurações distintas no par:** fica só o primeiro destaque, como no card.
- **Sem ingresso:** irrelevante, porque o card não exibe ingresso.
- **Sem unidade na formação:** legenda "Ifes · ilustração".
- **Unidade sem imagem própria:** ilustração genérica.
- **Nome oculto ou ausente na fonte:** sem zona de nome.
- **Caracteres acentuados e "ç":** renderizados com a fonte embutida, idênticos ao card.
- **Movimento:** em nenhum instante um texto em translação ou escala sai da área segura ou
  cobre outro texto.
- **Composição impossível:** falha explícita no desenvolvimento, nunca corte silencioso.
- **Pedido enquanto outro está em andamento:** não inicia segunda geração para o mesmo
  conteúdo.
- **Mudança de escolha de nome:** é conteúdo diferente e, portanto, outro vídeo.
- **Mudança no conteúdo da narrativa ou na versão do template:** o vídeo anterior não é
  reutilizado.
- **Sessão expirada durante a geração:** o vídeo só é entregue a uma sessão cuja própria
  composição, recalculada no servidor, corresponda a ele (FR-025). Sem sessão, vale o
  redirecionamento da 021.
- **Retenção vencida:** o vídeo precisa ser gerado de novo; nada fica guardado além dela.

## Requirements *(mandatory)*

### Functional Requirements

#### Acesso e lugar na experiência

- **FR-001**: O vídeo DEVE ser oferecido só na página "Minha trajetória no Ifes", nas mesmas
  condições de acesso da 021: sessão de Pessoa e Participação concluída ancorada em
  Conclusão sua. Sem essas condições, valem os mesmos redirecionamentos (021 FR-001,
  FR-002). [Arquitetura; 021]
- **FR-002**: O vídeo DEVE ser gerado só por ação explícita do egresso. Abrir a página NÃO
  DEVE iniciar geração. [Arquitetura; Const. XXII]
- **FR-003**: Como toda a 021, o vídeo DEVE existir só no modo de demonstração. O uso em
  produção depende das decisões pendentes herdadas e da DP-2201. [Arquitetura; 021 FR-069]

#### Entrada: composição visual do card

- **FR-004**: O vídeo DEVE ser produzido exclusivamente a partir da **composição visual do
  card**: os mesmos elementos, textos, posições e decisões de corte do card da 021,
  agrupados por zona, para a mesma narrativa e a mesma escolha de nome. [Solicitante; E1]
- **FR-005**: A composição visual DEVE ser projeção mecânica da composição do card. NÃO DEVE
  existir segundo modelo semântico da trajetória, nem regra de dado nova, nem frase nova.
  [Solicitante; 021 FR-014]
- **FR-006**: O renderizador de vídeo NÃO DEVE refazer layout, medir texto, quebrar linhas,
  decidir quais formações ou destaques aparecem, formatar números nem gerar texto. Ele só
  anima o que recebe. [Solicitante; E1, E2]
- **FR-007**: A composição visual DEVE ser serializável num formato estável e versionado,
  com a versão do contrato e a versão do template. Ela NÃO DEVE conter identificador
  interno, código de fonte, CPF, data de nascimento, contato, Resposta, dado declarado nem
  referência a entidades do domínio. [Arquitetura; Const. XVI]
- **FR-008**: Todos os ativos usados pelo vídeo (fontes, ilustrações, marca) DEVEM ser
  conhecidos antes da geração e versionados com o sistema. A geração NÃO DEVE buscar
  imagem, fonte ou qualquer recurso externo. [Solicitante]

#### Formato

- **FR-009**: O vídeo DEVE ter:
  - 1080 × 1920 px (9:16), orientação vertical;
  - 30 quadros por segundo;
  - vídeo H.264 em contêiner MP4, reproduzível nos navegadores e celulares comuns sem
    conversão;
  - imagem opaca, sem transparência;
  - **nenhuma faixa de áudio**.

  [Solicitante]
- **FR-010**: A duração DEVE ter alvo de 8 s e ficar entre 7 e 10 s. Passar de 8 s só é
  permitido para preservar a legibilidade, por exemplo com 4 formações exibidas. A duração
  é função da composição e nunca escolha do egresso. [Solicitante]

#### Sequência animada (storyboard)

- **FR-011**: O vídeo DEVE apresentar as zonas na ordem e nas janelas do storyboard-base:
  - abertura (0,0–0,7 s);
  - título e nome (0,7–1,7 s);
  - linha do tempo (1,7–5,0 s);
  - destaques (5,0–6,3 s);
  - fechamento e convergência para o card (6,3–8,0 s).

  As fronteiras valem para durações de 8 s, com variação máxima de ±0,3 s cada; os ajustes
  finos são do plan. Quando a legibilidade exigir duração maior (FR-010), só a janela da
  linha do tempo se alonga, e as fronteiras seguintes deslocam-se exatamente pelo mesmo
  acréscimo. As durações relativas de destaques e fechamento se mantêm. [Solicitante;
  analyze I1]
- **FR-012**: Na linha do tempo, cada formação exibida pelo card DEVE entrar como um nó
  (ano, curso, atributos), na ordem do card, em sequência. O traço entre os nós DEVE ser
  desenhado progressivamente, de cima para baixo. A linha "e mais N formações registradas",
  quando existir no card, DEVE entrar depois do último nó. [Solicitante; 021 FR-082]
- **FR-013**: Os destaques DEVEM aparecer só quando estiverem na composição do card, com os
  mesmos números e rótulos. Os números DEVEM aparecer com o valor final, sem contagem
  animada. Sem destaques, NÃO DEVE haver bloco, número nem zero, e a janela correspondente
  vira permanência do quadro final. [Solicitante; E7; 021 FR-078]
- **FR-014**: O quadro final DEVE ser a composição do card (mesmas zonas, posições, textos e
  ativos). DEVE permanecer estável por pelo menos 1 s, e nos últimos 1 a 1,3 s não deve
  haver movimento perceptível. [Solicitante]
- **FR-015**: Na demonstração, a indicação "Demonstração — dados fictícios" DEVE estar
  visível em todos os quadros, do primeiro ao último. [Arquitetura; 021 FR-037]
- **FR-016**: As animações DEVEM se limitar a:
  - opacidade;
  - translação;
  - escala;
  - desenho progressivo do traço;
  - transições curtas entre blocos.

  NÃO DEVEM ser usadas:
  - partículas;
  - efeitos 3D;
  - movimento de câmera complexo;
  - física exagerada;
  - filtros pesados;
  - animação decorativa que concorra com os dados.

  [Solicitante]
- **FR-017**: Em nenhum instante um texto DEVE sair da área segura do card (021 FR-072) nem
  cobrir outro texto. Durante as transições, só imagem, fundo e grafismo podem ocupar as
  faixas de topo e de base. [Solicitante; 021 FR-072]

#### Determinismo

- **FR-018**: A mesma composição visual com a mesma versão do template DEVE produzir o
  mesmo conteúdo visual quadro a quadro, dentro da tolerância de codificação definida no
  plan. A identidade byte a byte do arquivo NÃO é exigida. [Solicitante; Arquitetura]
- **FR-019**: Existe um único template, com versão identificada. Mudança visual no template
  DEVE gerar nova versão, o que invalida qualquer reaproveitamento anterior. [Solicitante]

#### Privacidade e conteúdo

- **FR-020**: O vídeo DEVE obedecer exatamente às regras de conteúdo compartilhável do card
  (021 FR-033 a FR-036 e FR-041):
  - NÃO DEVE conter situação profissional, renda, raça/cor, deficiência, Respostas,
    e-mail, telefone, CPF, data de nascimento, identificador interno, dado de Formação
    Declarada, forma de oferta, data completa, tempo decorrido nem ingresso;
  - NÃO DEVE conter elemento de documento oficial.

  [Solicitante; Const. XVI]
- **FR-021**: O nome DEVE aparecer no vídeo somente quando o egresso escolher incluí-lo, pela
  mesma escolha que vale para o card (021 FR-034), e somente quando a fonte informar nome.
  NÃO DEVE existir preferência de privacidade nova para o vídeo, e a escolha NÃO DEVE ser
  persistida como preferência. [Solicitante; DP-2103]
- **FR-022**: Expressões como "sua turma", "sua geração" ou "X pessoas se formaram com
  você" NÃO DEVEM aparecer. O vídeo só exibe textos que já estão no card, e o catálogo da
  021 já os veda. [Solicitante; 021 FR-061]
- **FR-023**: A imagem da abertura DEVE ser a do catálogo da 021, com a mesma legenda. NÃO
  DEVE ser apresentada como memória do período vivido pelo egresso. [Solicitante; 021
  FR-076; DP-2106]
- **FR-024**: O vídeo NÃO DEVE conter conteúdo gerado por IA, narração, voz sintética,
  música nem efeito sonoro. [Solicitante]
- **FR-025**: O vídeo DEVE ser entregue só a uma sessão de Pessoa elegível cuja própria
  composição visual, recalculada no servidor a cada requisição, corresponda ao vídeo. O
  cliente nunca informa qual vídeo quer, e nenhum identificador do vídeo é exposto.
  - Duas Pessoas com composição idêntica podem receber o mesmo arquivo: o conteúdo é o que
    cada uma já pode gerar.
  - NÃO DEVE existir página pública, link permanente, URL compartilhável, publicação em
    rede social nem integração com API de rede social.

  [Arquitetura; 021 FR-039; DP-2101; research R6; analyze I2]
- **FR-026**: O nome do arquivo baixado DEVE ser neutro (`minha-trajetoria-ifes.mp4`).
  [Const. XVI; 021 FR-038]
- **FR-027**: Registros de operação (logs, mensagens de erro, estado técnico) NÃO DEVEM
  conter nome, curso, unidade nem outro dado pessoal. Só fatos técnicos (por exemplo,
  "falha na geração"). [Const. XVI; 021 FR-045]

#### Ciclo de vida, execução e estado

- **FR-028**: O vídeo é derivado técnico temporário. NÃO DEVE existir entidade de domínio de
  vídeo, histórico de vídeos por Pessoa nem armazenamento permanente. [Solicitante; Const.
  XXII]
- **FR-029**: O sistema PODE reaproveitar um vídeo já gerado para a mesma composição visual e
  a mesma versão do template, durante uma retenção curta. Depois dela, o arquivo DEVE ser
  descartado. Como o vídeo pode conter o nome, o arquivo temporário é dado pessoal: fica
  inacessível fora da entrega do FR-025. [Solicitante; E5; DP-2202]
- **FR-030**: A geração NÃO DEVE manter uma requisição aberta por tempo imprevisível. O plan
  escolhe entre:
  - geração síncrona, quando o spike mostrar tempo previsível e aceitável;
  - estado técnico mínimo persistido, com processamento fora da requisição.

  [Solicitante; E4]
- **FR-031**: Quando a geração não for instantânea, o estado observável pelo egresso DEVE se
  limitar a **solicitado**, **processando**, **pronto** ou **falhou**. NÃO DEVE existir
  workflow além desses estados. [Solicitante]
- **FR-032**: O sistema NÃO DEVE iniciar geração duplicada para a mesma composição e a mesma
  versão do template enquanto houver uma em andamento ou um resultado pronto e retido. O
  número de gerações simultâneas DEVE ser limitado, de modo que pedidos repetidos não
  degradem a página. [Arquitetura; Const. XVI]
- **FR-033**: Nenhuma etapa da geração, da espera ou da falha DEVE alterar Participação,
  Resposta, Conclusão, narrativa ou card, nem impedir o acesso à página. O único estado
  gravado, se existir, é o técnico do FR-030. [Solicitante; Const. I, VIII; 021 FR-008]

#### Página

- **FR-034**: A seção do card DEVE oferecer "Gerar vídeo" quando o renderizador estiver
  disponível. Conforme o estado, a seção DEVE mostrar:
  - **solicitado ou processando:** "Estamos preparando seu vídeo…";
  - **pronto:** prévia do vídeo, "Baixar vídeo (MP4)" e, como melhoria progressiva,
    "Compartilhar vídeo";
  - **falhou:** mensagem compreensível e "Tentar novamente".

  [Solicitante]
- **FR-035**: Todo o fluxo DEVE funcionar sem JavaScript: pedir, ver o estado ao recarregar
  e baixar. Atualização automática do estado e compartilhamento nativo PODEM existir como
  melhoria progressiva e nunca são o único caminho. [Arquitetura; 021 FR-029, FR-073]
- **FR-036**: A prévia NÃO DEVE iniciar reprodução automática e DEVE ter controles
  acessíveis por teclado. O vídeo DEVE ter alternativa textual equivalente: a mesma
  descrição textual do card (021 FR-067). As mudanças de estado DEVEM ser anunciadas a
  tecnologias assistivas. [Const. XX, XXI]
- **FR-037**: Sem o renderizador no ambiente, a opção de vídeo NÃO DEVE aparecer, ou DEVE
  aparecer como indisponível, sem erro. Página e card continuam idênticos aos da 021.
  [Arquitetura; 021 FR-031]

#### Fronteiras e falhas explícitas

- **FR-038**: O domínio NÃO DEVE conhecer detalhes internos do renderizador. DEVE haver uma
  única fronteira: entra a composição visual e a versão do template, sai o vídeo ou a falha.
  NÃO DEVE ser criado framework genérico de renderização multimídia. [Solicitante; Const.
  V, XXII]
- **FR-039**: Quando a composição do card não puder representar a trajetória nem no mínimo
  da 021 (título, ao menos um curso e fecho), a geração DEVE falhar explicitamente,
  registrando o fato técnico. NÃO DEVE cortar informação em silêncio. [Solicitante; 021
  FR-082]
- **FR-040**: Para o MVP, DEVE existir exatamente um template. NÃO DEVEM existir catálogo de
  templates, editor, personalização de animação nem escolha de estilo pelo egresso.
  [Solicitante; Const. XXII]

### Matriz mínima de verificação automatizada

Cada caso é verificado sem inspeção humana de todos os quadros.

| Verificação | Casos |
|---|---|
| Resolução, fps, codec, contêiner, ausência de áudio, opacidade | Todos |
| Duração entre 7 e 10 s; 8 s ± 0,3 s com até 3 formações | 1, 2, 3, 4 e mais de 4 formações |
| Textos do vídeo = textos do card | Todos |
| Conteúdo vedado (FR-020, FR-022) ausente | Todos, incluindo a lista `VEDADAS` da 021 |
| Quadro final ≈ PNG do card (tolerância do plan) | Todos os casos de referência |
| Quadros-chave em ~1 s, ~4 s e final ≈ referência aprovada (tolerância, não pixel-perfect) | Casos de referência da 021 |
| Texto dentro da área segura e sem sobreposição nos quadros-chave e nas fronteiras das janelas | Nomes longos; 4 e mais de 4 formações; dois destaques |
| Rodapé de demonstração presente | Primeiro, intermediários e último quadro |
| Destaques ausentes sem bloco nem zero | Sem agregado |
| Um e dois destaques iguais aos do card | Um e dois agregados; apurações distintas |
| Nome presente só com escolha e nome disponível | Nome ligado, desligado e ausente na fonte |
| Ilustração genérica e legenda | Unidade sem imagem própria; formação sem unidade |
| Acentos e "ç" | Cursos e unidades acentuados |
| Composição impossível falha explicitamente | Caso forçado |
| Sem efeito colateral em dados de domínio | Pronto, falha e indisponível |
| Sem geração duplicada; reaproveitamento na retenção; invalidação por versão do template | Pedidos repetidos |
| Entrega só à sessão da mesma Pessoa; nome de arquivo neutro | Rotas |
| Fluxo sem JavaScript | Página |

### Key Entities *(include if feature involves data)*

- **Composição visual** (`ComposicaoVisual`; derivado, não persistido): o card da 021
  agrupado por zonas (abertura, título, linha do tempo, destaques, fechamento, rodapé), com
  elementos já posicionados e textos prontos. Mesma fonte do PNG. Não referencia Pessoa,
  Conclusão Acadêmica nem Resposta.
- **Template de vídeo** (artefato versionado, único): define só o tempo e o movimento de cada
  zona. Tem versão identificada (FR-019).
- **Vídeo gerado** (derivado técnico temporário): arquivo MP4 identificado pela combinação
  da composição visual e da versão do template. É retido por pouco tempo e nunca é
  histórico.
- **Estado técnico da geração** (só se o plan escolher execução assíncrona): solicitado,
  processando, pronto ou falhou, ligado à mesma identificação do vídeo. Não é entidade de
  domínio e não se liga a Participação nem a Resposta.

### Origem dos Dados *(include if feature reads, collects or exports data)*

| Dado no vídeo | Origem | Fonte ou regra | Tratamento de divergência |
|---|---|---|---|
| Curso, unidade, nível, modalidade, ano de conclusão | Institucional | `TrajetoriaNarrativa.compartilhavel` (021) | Nenhum: o vídeo replica o card |
| "e mais N formações registradas" | Derivado | Regra de corte do card (021 FR-082) | Idem |
| Números e rótulos dos destaques | Agregado | Destaques do card (021 FR-078) | Idem |
| Nome | Institucional | Só com escolha e nome disponível (021 FR-034) | Idem |
| Título, fecho, hashtag, legenda, rodapé | Texto fixo do catálogo | `catalogo.py` (021) | Idem |
| Imagem da abertura | Ativo institucional/decorativo | Catálogo de imagens (021 FR-076) | Legenda "· ilustração"; nunca memória pessoal |
| Tempo e movimento | Template | Versão do template | Nenhum dado |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% dos casos da matriz, o arquivo tem 1080 × 1920, 30 fps, H.264 em MP4,
  nenhuma faixa de áudio e duração entre 7 e 10 s. Com até 3 formações exibidas, a duração
  é de 8 s ± 0,3 s.
- **SC-002**: Em 100% dos casos de referência, o quadro final coincide com o PNG do card da
  mesma escolha de nome, dentro da tolerância definida no plan, e fica estável por pelo
  menos 1 s.
- **SC-003**: Em 100% dos casos, o conjunto de textos do vídeo é igual ao do card. Zero
  ocorrências de conteúdo vedado.
- **SC-004**: Em 100% dos casos de borda, nenhum texto sai da área segura nem se sobrepõe a
  outro nos quadros-chave e nas fronteiras das janelas do storyboard.
- **SC-005**: Com o renderizador indisponível, com falha ou com geração em andamento, 100%
  dos acessos à página exibem a trajetória e o card normalmente, e as contagens de
  Participações e Respostas não mudam.
- **SC-006**: No ambiente de demonstração de referência, o egresso tem o vídeo pronto em até
  60 s após o pedido. Um novo pedido do mesmo conteúdo dentro da retenção fica pronto sem
  nova geração. O plan confirma ou revisa o limite com o spike, com justificativa.
- **SC-007**: O fluxo de pedir, acompanhar e baixar é concluído sem JavaScript, por teclado,
  em largura de 320 px.
- **SC-008**: Antes do merge, o solicitante aprova os quadros-chave (~1 s, ~4 s e final) e
  os MP4 dos casos de referência. O vídeo é validado num celular real como story de teste.
  A validação no celular é manual e registrada em `validacao.md`.

## Assumptions

- A composição do card da 021 é a fonte da verdade visual. Agrupá-la por zonas é
  refatoração interna que não altera o SVG nem o PNG.
- A Feature 021 está mergeada (PR #30), e o contrato da narrativa continua na versão 1.
- Os casos de referência são os da 021 (`specs/021-minha-trajetoria-narrativa/evidencias/`).
- O spike do Remotion, no research, mede tempo, memória e tamanho das dependências antes de
  fixar a execução.
- O ambiente de demonstração tem capacidade para executar o renderizador localmente. Em
  ambiente sem ele, vale o FR-037.
- A integração contínua passa a precisar do renderizador para um teste de fumaça. Os demais
  testes rodam sem codificar vídeo.
- A validação no celular real usa conta de teste, como na 021.

## Relação com outras features

- **021 (fonte):**
  - Narrativa, compartilhável, regras de corte, catálogo de textos, imagens, fontes, tema e
    escolha do nome são reutilizados sem mudança de comportamento.
  - Mudança interna: a composição do card passa a ser exposta agrupada por zona.
  - Nota de revisão a aplicar: o `contracts/card.md` e o `contracts/narrativa.md` registram
    que a composição visual é consumida pelo vídeo.
- **021 FR-014** previa um renderer de vídeo consumindo o contrato serializável. Esta spec
  precisa o ponto: o vídeo consome a composição do card, derivada do contrato, e não o
  contrato bruto.
- **006, 008, 014, 018:** nenhum impacto. A 022 só lê e reaproveita a sessão.
- **011, 012, 013:** nenhum dado da 022 entra em acompanhamento, snapshot ou exportação.
- **020:** independente.
- **ADR 0006:** reservava o Chromium headless à 022. O plan registra um ADR próprio para o
  renderizador de vídeo.

## Invariantes Constitucionais Afetados *(mandatory)*

- **I e VIII — Longitudinalidade e preservação histórica**: a 022 só lê. Nenhuma
  Participação, Resposta ou Conclusão é criada ou alterada (FR-033).
- **III — Institucional ≠ derivado ≠ declarado**: o vídeo exibe só o que o card exibe, com a
  mesma origem. Nenhum dado declarado (FR-020).
- **V — Integrações desacopladas**: renderizador atrás de uma única fronteira (FR-038).
- **XVI — Privacidade**:
  - mesmo subconjunto compartilhável da 021;
  - nome só por escolha;
  - arquivo temporário tratado como dado pessoal;
  - entrega só à sessão da Pessoa;
  - logs sem dados pessoais (FR-020 a FR-029).
- **XX e XXI — Acessibilidade e mobile**: fluxo sem JavaScript, sem autoplay, alternativa
  textual, estados anunciados (FR-035, FR-036).
- **XXII — YAGNI**:
  - um template;
  - sem entidade de vídeo nem histórico;
  - sem broker nem fila em arquivos;
  - sem framework de mídia;
  - estado técnico só se necessário (FR-028 a FR-032, FR-040).
- **XXIV — Stack**: o renderizador de vídeo é dependência nova de runtime, a registrar em ADR
  e em Complexity Tracking no plan.
- **XXVII — Migrações**: só se o plan escolher estado técnico persistido. É aditiva e não toca
  tabelas existentes.
- **XXIX — Hipóteses**: compartilhamento, marca, nome, agregados, imagens, fecho, licença e
  retenção seguem como decisões pendentes, com tratamento provisório restrito à
  demonstração.

## Fronteira do NIAE *(include if the feature goes beyond longitudinal tracking)*

1. **Pertence ao domínio de acompanhamento?** Em parte, como a 021: é uma forma a mais da
   devolutiva da participação, sem dado novo.
2. **É necessária ao ciclo de acompanhamento?** Não. É hipótese de produto para adesão e
   divulgação. Por isso fica restrita à demonstração (FR-003).
3. **Existe solução institucional mais adequada?** A comunicação institucional (ACS) poderia
   produzir peças em vídeo, mas não personalizadas. A relação com o Portal do Egresso segue
   pendente (DP-2108).
4. **Integração seria suficiente?** A composição visual serializada permite que outro sistema
   renderize o mesmo vídeo sem absorver o domínio.
5. **Aumenta o acoplamento do núcleo?** Não. O renderizador fica atrás de uma fronteira, e o
   domínio não muda.

## Out of Scope *(mandatory)*

- **Conteúdo gerado:** IA generativa, imagens geradas por IA, narração, TTS, voz sintética,
  música, escolha de trilha, efeitos sonoros e qualquer áudio.
- **Templates e edição:**
  - mais de um template ("cinco estilos animados");
  - catálogo, marketplace ou editor de templates;
  - personalização livre da animação ou animações por usuário.
- **Conteúdo do egresso:** upload de foto, avatar, vídeo do próprio egresso, stickers,
  filtros e recorte manual.
- **Redes sociais:** publicação automática no Instagram ou em outra rede, OAuth com redes
  sociais, analytics de visualização, tracking.
- **Formatos:** feed 4:5, vídeo horizontal, legendas automáticas, transparência.
- **Infraestrutura e armazenamento:**
  - entidade de domínio de vídeo;
  - histórico de vídeos;
  - armazenamento permanente;
  - versionamento de render por usuário.
- **Filas:** Celery, RabbitMQ, Redis como broker e fila em sistema de arquivos.
- **Regras e dados:**
  - regra de negócio ou de dado no renderizador;
  - segundo layout;
  - nova preferência de privacidade;
  - qualquer dado que o card da 021 não exiba;
  - contador animado nos números.

## Decisões Pendentes *(mandatory — write "Nenhuma" if empty)*

### Herdadas, explicitamente preservadas

- **DP-2101**: compartilhamento de representação da trajetória com o nome do Ifes. Passa a
  cobrir também o vídeo. Tratamento provisório: download e menu do dispositivo, só na
  demonstração.
- **DP-2102**: uso da marca do Ifes em peça compartilhável. O vídeo usa a mesma assinatura do
  card, só na demonstração.
- **DP-2103**: nome civil × nome social. O vídeo segue a escolha do card.
- **DP-2105**: exibição dos agregados. O vídeo exibe só os destaques do card.
- **DP-2106**: acervo de imagens por unidade. Só a ilustração genérica própria.
- **DP-2108**: relação com o Portal do Egresso.
- **DP-2110**: fecho e `#SouEgressoIfes`. Os mesmos textos do catálogo.
- **008/DP-801**: identidade visual definitiva.

### Novas

- **DP-2201** — DECISÃO PENDENTE: aceite institucional, antes de qualquer uso em produção,
  de três pontos:
  - a licença e os termos do Remotion (software *source-available*, com licença gratuita
    para organizações *non-profit/not-for-profit* segundo a documentação atual, e termos
    que mudam na versão 5.0);
  - eventuais licenças de codec H.264;
  - a operação do navegador headless no servidor.
  - Instância competente: DTI, com a procuradoria ou a assessoria jurídica.
  - Impacto: FR-003, FR-009.
  - Tratamento provisório: uso só na demonstração. Não bloqueia a spec, o plan nem a
    demonstração.
- **DP-2202** — DECISÃO PENDENTE: prazo de retenção de arquivos temporários com dado pessoal
  (o vídeo pode conter o nome), em ambiente real.
  - Instância competente: encarregado de dados, com a DTI.
  - Impacto: FR-029.
  - Tratamento provisório: na demonstração, retenção técnica curta, fixada no plan (da
    ordem de horas, nunca mais de 24 h), com descarte automático.
