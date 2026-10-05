# Auditoria — Feature 022: Minha Trajetória em vídeo

Data: 2026-10-05. Escopo: auditoria arquitetural curta, antes do `/speckit-specify`. Não
redesenha o domínio da trajetória. Base: Feature 021 (PR #30), ADR 0001 e ADR 0006.

**Conclusão:** havia **um fork material**, o motor de renderização (§13).

**Decisão do solicitante (2026-10-05):**

- **A**: o Remotion anima a composição visual produzida pela 021;
- **B** descartada: não haverá segundo layout em React;
- **C** mantida só como spike e fallback técnico, não como arquitetura da 022.

A estratégia de execução (§4) foi reaberta para comparação no research e no plan.

---

## 1. O que da 021 é reutilizado

| Peça da 021 | Onde | Uso na 022 |
|---|---|---|
| `TrajetoriaNarrativa.compartilhavel` | `narrativa/contrato.py` | Única fonte de dados do vídeo. Mesmas regras do card (FR-033 a FR-036) |
| Composição por zonas | `card.compor()` → `Composicao` | Elementos SVG **já posicionados**, com `class` por zona (`abertura`, `marca`, `titulo`, `nome`, `ano`, `curso`, `detalhe`, `traco`, `no`, `destaque`, `numero`, `rotulo`, `fecho`, `hashtag`, `rodape`, `apuracao`, `faixa`…) |
| Quebra de linha medida | `metricas.py`, `linhas_curso`, `linhas_detalhe` | Mesmas quebras, sem segunda medição |
| Regras de corte e ocupação | `compor()` (FR-080, FR-082) | Mesmas formações exibidas, mesmo "e mais N", mesmos destaques |
| Tema, fontes, ativos | `TEMA_CARD`, Open Sans (OFL), `ifes-generica.svg`, `assinatura.svg` | Linguagem visual idêntica; todos os ativos versionados no repositório |
| Textos | `catalogo.py` (`TITULO`, `FECHO`, `HASHTAG`, `CARD_DEMO`, legenda, rótulos) | Nenhum texto novo é necessário |
| Regra do nome | rota: `nome=1` e `nome_disponivel` (FR-034) | A mesma escolha da página vale para o vídeo |
| Rede de segurança | `catalogo.VEDADAS`, testes de conteúdo vedado | Reaplicada ao texto do vídeo |

**Achado principal.** O storyboard pedido percorre exatamente as zonas do card, na mesma
ordem: abertura → título → linha do tempo → destaques → fecho/rodapé. O vídeo pode ser
literalmente "o card ganhando movimento": cada zona entra no seu instante e o **quadro
final é o card**. Isso garante a convergência visual por construção, sem segundo layout.

Spike (macOS arm64, fora do repositório): os elementos de `compor()` agrupados por zona,
com `opacity` e `translate` por grupo, rasterizados pelo `png_de` atual → quadros corretos
a **~106 ms por quadro** (240 quadros ≈ 25 s num núcleo).

## 2. Formato consumido

- `serializar(narrativa)["compartilhavel"]` é **necessário, mas não suficiente**:
  - faltam os textos prontos que o card monta (título em duas linhas, legenda da imagem,
    "e mais N", número formatado "1.234", linhas do rodapé, marca de demonstração);
  - faltam as decisões de layout (quais formações cabem, se os destaques ficam, arranjo);
  - o nome não está no compartilhável, por desenho (a rota o acrescenta).
- Recriar isso no renderizador violaria a garantia da 021: "o renderizador não gera frase
  nem aplica regra de dado".
- **Decisão:** a entrada do vídeo é a **`ComposicaoVisual`**: a projeção mecânica de
  `card.compor()`, agrupada por zona (abertura, título, linha do tempo, destaques,
  fechamento, rodapé). Não há modelo semântico novo nem regra nova. O PNG e o vídeo são
  duas renderizações da mesma composição.

```
TrajetoriaNarrativa → card.compor() → ComposicaoVisual (zonas) → PNG (resvg) | MP4 (Remotion)
```

```json
{
  "versao_contrato": 1,
  "template": "trajetoria-v1",
  "largura": 1080, "altura": 1920, "fps": 30, "duracao_quadros": 240,
  "formacoes_exibidas": 2, "destaques": true,
  "zonas": [
    {"zona": "abertura", "elementos": [{"tag": "g", "atributos": {...}, "interior": "<svg…>"}]},
    {"zona": "titulo", "elementos": [{"tag": "text", "atributos": {...}, "texto": "Minha trajetória"}]},
    {"zona": "linha_do_tempo", "nos": [[...], [...]], "traco": [...]},
    {"zona": "destaques", "elementos": [...]},
    {"zona": "fecho", "elementos": [...]},
    {"zona": "rodape", "elementos": [...]}
  ]
}
```

- Ajuste necessário na 021: `compor()` passa a expor os elementos **agrupados por zona** (hoje
  é uma lista plana com `class`). Mudança interna, sem efeito no SVG do card.
- `interior` só carrega ativos versionados (imagem do catálogo, assinatura). Nada é baixado
  durante o render (pedido §9).

## 3. Fronteira Python ↔ Node

```
view (sessão, nome=1)                       ← já existe na 021
  └─ video.py                               ← único módulo Python que conhece o renderizador
       └─ ComposicaoVisual serializada (JSON)
            └─ processo Node: projeto Remotion isolado, um template
                 └─ MP4
```

- O projeto Remotion fica isolado num diretório próprio, com `package.json` e lockfile.
  Recebe só o JSON da composição e não conhece `Pessoa`, `ConclusaoAcademica` nem
  `Resposta`.
- **Nenhuma regra de negócio no Remotion:** ele só anima o que recebe (tempo, opacidade,
  translação, escala, traço).

- Um módulo, `trajetoria/narrativa/video.py`, no mesmo padrão de `rasterizacao.py`
  (ADR 0006): única porta, devolve "indisponível" quando o renderizador falta, nunca
  derruba a página.
- Nenhum comando de renderizador fora desse módulo e do worker.
- Sem framework genérico de mídia: uma função, um template.

## 4. Execução

- **Não existe** fila, Celery, worker nem infraestrutura de jobs. O cache é `LocMemCache`
  por processo (018, só demonstração). ADR 0001: filas só com caso concreto.
- O tempo de render do Remotion ainda não foi medido. O spike C deu ~25 s com um núcleo,
  sem codificação.
- **Decisão (revisão de 2026-10-05):** a forma de execução **não está fixada**. O
  research/plan compara duas soluções mínimas, a partir de um spike do Remotion:

| Opção | Quando |
|---|---|
| 1. Render síncrono | Se o spike mostrar tempo previsível e aceitável para uma requisição |
| 2. Estado técnico mínimo persistido (`SOLICITADO` → `PROCESSANDO` → `PRONTO` ou `FALHOU`) + worker por comando de gerenciamento | Se o assíncrono for realmente necessário. Uma tabela técnica pequena, com migration, é mais confiável que um protocolo de arquivos |

- **Rejeitados:**
  - **pasta de pedidos como fila:** recria em filesystem concorrência, abandono, retry,
    limpeza e reinício (proposta da primeira versão desta auditoria, retirada);
  - **thread no processo web**;
  - **Celery/RabbitMQ/Redis** sem necessidade demonstrada.
- O estado técnico, se existir, **não é entidade de domínio** `Video` e não guarda
  histórico funcional.

## 5. Arquivo e cache

| Opção | Avaliação |
|---|---|
| A. Sob demanda, resultado temporário | Suficiente se o render for síncrono e rápido. Com render assíncrono, o resultado precisa existir até o download: vira B |
| **B. Cache técnico por hash (composição + versão do template)** | **Aceito como otimização técnica.** Mesmo pedido não renderiza de novo; TTL curto (ex.: 24 h, a fixar no plan); limpeza pelo worker; não é histórico |
| C. Armazenamento permanente | Rejeitado: cria histórico por usuário sem necessidade |

- O MP4 pode conter o nome: tratá-lo como dado pessoal. Diretório fora de qualquer raiz
  servida; entrega só pela rota da sessão, que recalcula o hash (sem URL por hash,
  preservando a 021 FR-039); nada de conteúdo em log.

## 6. Deploy

- **Não há ambiente de produção** (`settings.py`; tudo é demonstração local). O impacto é
  sobre desenvolvimento, CI e requisitos para um deploy futuro.

| Item | Remotion (alternativas A/B) | Python + FFmpeg (alternativa C) |
|---|---|---|
| Runtime novo | Node ≥ 18 (22 LTS) + projeto npm isolado | Nenhum |
| Navegador | Chrome Headless Shell (~100–150 MB), provisionado antes, nunca baixado no render | Nenhum |
| Codificador | FFmpeg embutido nos pacotes `@remotion/compositor-*` | Binário FFmpeg do sistema (apt) |
| Bibliotecas de sistema | ~14 pacotes no Ubuntu (libnss3, libgbm…); Alpine sem suporte | Só as do FFmpeg |
| Tamanho estimado | node_modules ~200 MB + navegador | ~80–100 MB (ffmpeg via apt) |
| CPU / memória por render | Multinúcleo; ~1–2 GB com concorrência (estimativa a medir) | 1 núcleo ~25 s; paralelizável; < 300 MB |
| Licença | Remotion: gratuita para "non-profit or not-for-profit organization"; empresas > 3 pessoas pagam. Ifes (autarquia) provavelmente elegível, **a confirmar**; a 5.0 muda os termos | FFmpeg (LGPL/GPL conforme build) |

Medidas do Remotion são estimativas de documentação; precisam de spike no plan.

## 7. CI

- Hoje: um job `testes` (Python 3.13 + Postgres 16), exigido pelo ruleset da `main`.
- Remotion: `setup-node`, `npm ci` com cache, bibliotecas de sistema, navegador e um render
  de fumaça. Estimativa: +2 a 4 min por execução.
- Python: `apt-get install ffmpeg` e o render de fumaça. Estimativa: +30 a 60 s.
- Em ambos: testes de conteúdo e de tempo de animação rodam sem codificar vídeo; um teste
  de integração codifica um MP4 curto e inspeciona com `ffprobe`. Sem o renderizador, o
  teste é pulado localmente, como o do PNG.

## 8. Riscos operacionais

- **Licença do Remotion** para o Ifes (DP institucional).
- **Chromium** como superfície de segurança e atualização contínua no servidor.
- **Custo e abuso:** render custa segundos de CPU; limitar a um render simultâneo e um
  pedido por hash.
- **Disco:** TTL e limpeza obrigatórios; MP4 de 8 s ≈ 1–3 MB.
- **Dado pessoal em arquivo temporário** (nome, cursos).
- **Determinismo:** os quadros são determinísticos; os bytes do MP4 podem variar entre
  versões do codificador. Testar conteúdo, não bytes.
- **Compatibilidade com redes:** H.264, `yuv420p`, `+faststart`, 30 fps, sem faixa de áudio.

## 9. Storyboard (~8 s, 30 fps, 240 quadros)

Versão revista pelo solicitante.

| Tempo | Quadros | Zona da composição | Movimento |
|---|---|---|---|
| 0,0–0,7 s | 0–21 | Abertura (unidade), marca, legenda | Imagem com escala 1,04 → 1,00 e opacidade; marca e legenda entram |
| 0,7–1,7 s | 21–51 | Título e nome (se escolhido) | "Minha trajetória" / "no Ifes" sobem com opacidade |
| 1,7–5,0 s | 51–150 | Linha do tempo | O traço se desenha de cima para baixo; cada nó (ano, curso, detalhe) entra em sequência. A janela é dividida pelas formações exibidas; "e mais N" por último |
| 5,0–6,3 s | 150–189 | Destaques | Cartões entram; **números estáticos**, sem contador |
| 6,3–8,0 s | 189–240 | Fechamento | Fecho e `#SouEgressoIfes` entram; a composição converge para o card. Nos **últimos 1–1,3 s quase nada se move**: o quadro final é o card |

- Sem destaques: a duração total se mantém em 8 s e o tempo vira permanência do quadro
  final.
- **Rodapé e "Demonstração — dados fictícios" visíveis em todos os quadros**: quem vê só um
  trecho do vídeo também precisa saber que é demonstração (021 FR-037).
- **Sem contador:** não agrega e aumenta o ruído. Além disso, mostraria números
  intermediários que não são fatos.
- **Duração:** alvo de 8 s; até 10 s só para preservar a legibilidade (por exemplo, com 4
  formações).

## 10. Casos extremos

| Caso | Comportamento |
|---|---|
| 1 formação | Sem traço; o nó usa a janela inteira |
| 4 formações | ~0,8 s por nó |
| Mais de 4 | O que `compor()` decidir: até 4 exibidas + "e mais N" |
| Curso ou unidade longos | Linhas já quebradas; o vídeo não remede |
| Sem agregado / um / dois | Destaques ausentes / um cartão / par (regras da 021) |
| Sem ingresso | Irrelevante: o card não exibe ingresso |
| Unidade sem imagem própria | Imagem genérica, legenda "Unidade X · ilustração" |
| Nome oculto | Zona do nome ausente |
| Acentos | Open Sans embutida em ambos os motores |

- O layout não pode estourar, porque é o do card. O risco novo é o **movimento**: teste de
  caixa delimitadora em todos os quadros-chave, com texto sempre dentro da área segura.
- Se `compor()` não couber nem no mínimo (título, um curso, fecho), o render **falha
  explicitamente**, sem cortar em silêncio.

## 11. Limite da 022

- **Dentro:**
  - um template de ~8 s;
  - MP4 H.264 1080 × 1920, 30 fps, sem áudio;
  - execução síncrona ou assíncrona com quatro estados, conforme o spike (§4);
  - cache técnico com retenção curta;
  - na página: "Gerar vídeo", "Estamos preparando seu vídeo…", "Baixar vídeo" e
    compartilhamento nativo como melhoria progressiva;
  - testes de conteúdo e de mídia.
- **Fora:** tudo do §18 do pedido, mais:
  - nova regra de privacidade;
  - entidade de domínio `Video`;
  - histórico;
  - fila em filesystem;
  - Celery/RabbitMQ;
  - regra de negócio dentro do Remotion.
- **Falha do vídeo** não afeta Participação, Respostas, narrativa, PNG nem o acesso à
  página.

## 12. Riscos de overengineering

| Risco | Contenção |
|---|---|
| Segundo layout (React) divergente do card | Entrada = zonas posicionadas da 021 |
| "Plataforma de vídeo" ou framework de mídia | Uma função e um template |
| Fila/broker | Síncrono, ou estado técnico mínimo + comando de gerenciamento |
| Motor de animação próprio (alternativa C) | Animação é do Remotion; C fica como spike |
| Entidade e histórico de vídeos | Cache por hash com retenção curta |
| Catálogo de templates | Constante `template = "trajetoria-v1"` |
| Contador, partículas, câmera | Fora; só opacidade, translação, escala e traço |
| Golden pixel-perfect | Quadros-chave comparados com tolerância e quadro final contra o PNG do card |

## 13. Fork material: motor de renderização

O pedido parte do Remotion. A auditoria mostra que a 021 já tem tudo o que o vídeo exige,
menos o codificador. Por isso o motor é uma decisão do solicitante.

| | **A. Remotion anima o card** | B. Remotion com layout próprio | **C. Python anima o card** |
|---|---|---|---|
| Entrada | Zonas de `compor()` (JSON) | `compartilhavel` | Zonas de `compor()` (em processo) |
| Layout | Python (021) | React/CSS (**segundo layout**) | Python (021) |
| Animação | `interpolate` do Remotion, por zona | Remotion | Funções de easing em Python sobre `opacity` e `transform` |
| Quadros | Chrome Headless Shell | Chrome | `resvg` (já em produção na 021) |
| Codificação | FFmpeg embutido | FFmpeg embutido | FFmpeg do sistema |
| Infra nova | Node, npm, Chrome, ~14 libs | Idem | Só FFmpeg |
| Quadro final = card | Por construção | Só por disciplina (medição de texto diverge) | Por construção, bytes do PNG |
| Licença | Remotion (DP) | Remotion (DP) | Sem pendência |
| Prévia de design | Remotion Studio | Studio | Quadros-chave em PNG (como as referências da 021) |
| Evolução | Templates mais ricos, mesma entrada | — | Trocar para A depois custa só o renderizador |

**Recomendação inicial da auditoria: C.** **Decisão do solicitante: A.**

- C começaria um motor de animação próprio em Python, que cresceria com o segundo
  template (easing, máscaras, stagger, transições, cenas): justamente o que o Remotion já
  resolve.
- A mantém a melhor descoberta desta auditoria: o Remotion **não refaz o layout**, só anima
  as zonas, e o quadro final é o card da 021.
- **Licença:** a FAQ atual do Remotion declara organizações non-profit/not-for-profit
  elegíveis à Free License. O Remotion é *source-available*, não open source OSI. Fica
  registrada uma **decisão institucional pré-produção** sobre o aceite da licença, dos termos
  e de eventuais licenças de codec H.264 (que existiriam também em C). Isso não bloqueia a
  spec nem a demonstração.
- C fica como spike e fallback técnico documentado.

Argumentos da recomendação inicial, mantidos para registro:

- O MVP precisa provar o valor do vídeo, não de uma plataforma de animação.
- As animações pedidas (opacidade, translação, escala, traço) são primitivas do SVG que o
  `resvg` já renderiza. O spike comprovou isso com as zonas reais.
- Evita Node, Chromium, licença e cerca de 14 bibliotecas de sistema antes de existir
  produção.
- **Se o Remotion for requisito** (ferramenta desejada pela equipe, Studio ou templates
  futuros): **A**. Ela mantém um único layout, e o Node só anima e codifica.
- **B não é recomendada:** recria em React a medição de texto, o corte e a ocupação da 021,
  com risco real de overflow silencioso e divergência do card.

---

Implementação: ver [validacao.md](../../specs/022-minha-trajetoria-video/validacao.md).
