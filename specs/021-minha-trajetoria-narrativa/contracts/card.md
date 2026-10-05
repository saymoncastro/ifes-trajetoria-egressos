# Contrato: card editorial vertical (9:16, PNG)

Este contrato cobre os FR-031 a FR-041, FR-065 a FR-067, FR-072 a FR-083 e o SC-015. O
desenho técnico está nas seções R10, R11 e R19 a R21 do [research](../research.md).

**Revisão de 2026-10-05.** O contrato deixou de ser lista de conteúdo e passou a descrever
a **composição editorial**. Base:
[auditoria de convergência visual](../../../docs/auditorias/2026-10-04-021-convergencia-visual.md),
com as decisões do solicitante:

- **V1:** assinatura oficial na demonstração;
- **V2:** ilustração vetorial própria;
- **V3:** fecho com `#SouEgressoIfes`.

**Foco:** compartilhamento em rede social no formato vertical, especialmente o story do
Instagram.

- O **PNG** é o artefato principal.
- O **SVG** é a representação-base e só é oferecido quando o PNG estiver indisponível.

## Entrada

- `TrajetoriaNarrativa.compartilhavel`.
- `tema`: `TEMA_CARD` (próprio, derivado da marca).
- `nome: str | None`, preenchido só com `nome=1` e `nome_disponivel`.
- `imagem`: a entrada do catálogo escolhida pela unidade da primeira formação exibida, ou a
  genérica.

## Quadro

| Item | Regra |
|---|---|
| Dimensões | **1080 × 1920 px (9:16)** |
| Área segura | Todo texto entre y = 270 e y = 1650, com 90 px de margem lateral (orientação da Meta para stories) |
| Fora da área segura | Só imagem, fundo ou grafismo: no topo, a imagem da abertura em sangria; na base, a faixa inferior |
| Corpo | Título ≥ 80 px; ano e número ≥ 44 px; ≥ 40 px no restante do conteúdo (curso, nome, fecho, "e mais N"); ≥ 30 px no texto de apoio (atributos em 36, rótulos dos destaques, legenda e hashtag); 26–30 px no rodapé e na proveniência |
| Contraste | WCAG 2.1 AA de todo texto, medido no tamanho em que o story aparece no celular (360 px de largura, ~1/3 do card). O verde da marca (3,1:1 no creme) só no grafismo e no título, que continua texto grande; o ano usa `marca_escura` (`#257a33`, 4,8:1) |

## Zonas, de cima para baixo (FR-074)

| Zona | Conteúdo | Regras |
|---|---|---|
| **Abertura** | Imagem do catálogo em sangria total, de y = 0 até uma borda em onda. **Marca oficial** sobre pílula branca no topo da área segura. Legenda em pílula escura no pé da imagem ("Unidade Serra · ilustração"; "Ifes · ilustração") | Borda inferior entre y = 420 (21,9% do quadro) e y = 890, pelo espaço livre (FR-080). A legenda divide a faixa da marca quando não colide com ela na horizontal; senão, a abertura cresce para a legenda caber abaixo da marca. A legenda nunca tem ano (FR-076) |
| **Título** | "Minha trajetória" (verde profundo) / "no Ifes" (verde marca), ≥ 80 px, negrito. Nome opcional abaixo, em 44 px | O nome só entra por escolha (FR-034) e nunca é truncado |
| **Linha do tempo** | Um nó por formação exibida e traço ligando os nós (com 2 ou mais). **Ano em destaque** (44 px, verde marca), curso em 44 px negrito, atributos "unidade · nível · modalidade" em 36 px | Ordem e relações do FR-019. Atributos quebrados só entre " · ". Sem ano, o nó fica sem rótulo de ano |
| **Excedente** | "e mais N formações registradas" | Quando houver formações não exibidas (FR-082) |
| **Destaques** (P2) | Até **um par** de cartões brancos com filete verde: **número ≥ 80 px** e rótulo de no máximo 2 linhas ("conclusões deste curso" / "na unidade Serra em 2022"; "conclusões registradas" / "na unidade Serra em 2022") | O par é o da primeira formação com agregado. **Arranjo:** lado a lado quando número e rótulos cabem na meia largura; senão, um cartão por linha, com o número à esquerda e os rótulos alinhados depois do maior número; se um rótulo não couber numa linha nem assim, os destaques saem (a página mostra a frase completa). Só entram se couberem (FR-078, FR-082) |
| **Fecho** | "Essa história também é minha." (46 px, negrito) e a pílula `#SouEgressoIfes` | Texto fixo do catálogo (FR-079; DP-2110) |
| **Rodapé** | "Instituto Federal do Espírito Santo"; "Demonstração — dados fictícios"; "Dados institucionais apurados em DD/MM/AAAA" (só com destaque) | 26–30 px, texto suave, ancorado na base da área segura. Instituição e demonstração na mesma linha, separadas por " · ", quando cabem. A proveniência aparece só aqui |
| **Faixa inferior** | Verde profundo com grafismo de quadrados | Sem texto |

## Ocupação e corte

- **Ocupação (FR-080):** dentro da área segura, nenhuma faixa vazia contínua passa de 160
  px nos casos de referência. A abertura cresce para ocupar o espaço livre; acima do
  máximo, a sobra se divide entre os dois lados do conteúdo.
- **Corte (FR-082):**
  1. abertura até o mínimo;
  2. retirada dos destaques;
  3. formações convertidas em "e mais N", com até 4 exibidas, tantas quantas couberem.

  Título, nome, curso e fecho nunca são cortados.

## Conteúdo vedado (FR-035, FR-036)

O card não pode conter:

- forma de oferta, data completa, tempo decorrido ou ingresso;
- Resposta ou qualquer dado declarado;
- CPF, data de nascimento ou contato;
- brasão, selo, assinatura de autoridade, QR, identificador, número ou data de emissão;
- "certificado", "comprovante" ou "declaração";
- foto pessoal;
- imagem apresentada como do período do egresso.

A **marca do Ifes** (assinatura visual) é identidade, não autenticação (FR-075).

## Catálogo de imagens (FR-076)

| Campo | Regra |
|---|---|
| `unidade` | Nome exato da unidade, ou `None` para a genérica, que é obrigatória |
| `arquivo` | Ativo versionado no app |
| `tipo` | "ilustração" ou "fotografia" |
| `origem`, `licenca` | Obrigatórios. Para "fotografia", só entram com licença registrada (DP-2106) |

- **Na demonstração:** uma única entrada genérica, a ilustração vetorial própria, com
  `origem = "Trajetória Ifes"` e `licenca = "própria"`.
- **Legenda:** "Unidade {unidade} · {tipo}" quando a formação tem unidade; senão, "Ifes ·
  {tipo}". A unidade da legenda é a da **formação**, não a da imagem: a genérica não
  representa nenhuma unidade real.

## Garantias técnicas

- **SVG:**
  - mesma entrada, mesmos bytes;
  - `<title>` e `<desc>` textuais (FR-067);
  - `font-family="Open Sans, system-ui, sans-serif"`.
- **PNG:**
  - rasterizado do mesmo SVG, com Open Sans Regular e Bold embutidas e sem as fontes do
    sistema;
  - 1080 × 1920;
  - reprodutível no mesmo ambiente.
  - Na indisponibilidade, `png_de` devolve `None` e a página cai para o SVG.
- **Entrega:**
  - PNG `inline` com nome `minha-trajetoria-ifes.png`;
  - download pelo atributo `download`;
  - SVG `attachment`;
  - sem cache e nada guardado.

## Na página (FR-073)

- **Prévia:** a própria PNG.
- **"Incluir meu nome no card":** por GET, sem JavaScript.
- **"Baixar imagem (PNG)".**
- **"Compartilhar imagem":** melhoria progressiva. Os destinos do menu dependem do
  aparelho.

## Referências visuais

- **Protótipos (esboços):** `docs/auditorias/evidencias-021-visual/proto-*.png`.
- **Referência aprovada:** `specs/021-minha-trajetoria-narrativa/evidencias/referencia-*.png`,
  gerados pelo renderer e aprovados pelo solicitante antes do merge (SC-015, item 9).

## Composição por zonas (Feature 022)

`card.compor()` também expõe a composição agrupada por zona (`Composicao.zonas`: abertura,
título, linha do tempo com um nó por parte, destaques com um cartão por parte, fecho,
rodapé). O vídeo da 022 anima exatamente essas partes
([composição visual](../../022-minha-trajetoria-video/contracts/composicao-visual.md)).

- A lista plana `elementos` e o SVG do card **não mudam**: teste de regressão byte a byte
  em `tests/narrativa/test_card_zonas.py`.
- `Composicao.cabe` é falso quando nem o mínimo coube. O card mantém o comportamento acima;
  o vídeo recusa a composição (022 FR-039).

## Temas (P3, FR-065)

- Um tema é só um conjunto de tokens e grafismos sobre as mesmas zonas.
- O texto é idêntico entre temas.
