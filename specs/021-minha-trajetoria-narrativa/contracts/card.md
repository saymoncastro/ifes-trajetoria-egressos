# Contrato: card para rede social (vertical 9:16, PNG)

Este contrato cobre os FR-031 a FR-041, FR-065 a FR-067, FR-072 e FR-073. O desenho
técnico está nas seções R8 a R11 do [research](../research.md).

**Foco:** compartilhamento em rede social no formato vertical, especialmente o story do
Instagram.

- O **PNG** é o artefato compartilhável principal.
- O **SVG** é a representação-base de onde o PNG sai. Só é oferecido quando o PNG estiver
  indisponível.

## Entrada

- `TrajetoriaNarrativa.compartilhavel`.
- `tema`: só `"padrao"` no P1.
- `nome: str | None`: preenchido só com `nome=1` e `nome_disponivel`.

## Formato e composição

| Item | Regra |
|---|---|
| Dimensões | **1080 × 1920 px (9:16)**: story do Instagram e status de outras redes (FR-040) |
| Área segura | Todo `<text>` entre y = 270 e y = 1570, com 90 px de margem lateral. As faixas de topo (0–270) e base (1570–1920) recebem só fundo ou grafismo, porque a interface das redes cobre essas áreas (FR-072) |
| Corpo de texto | Mínimo de 40 px (título, 64 px) na escala 1080, legível no celular |
| Contraste | WCAG 2.1 AA entre os tokens de texto e de fundo |

## Conteúdo permitido, e só ele

| Elemento | Regra |
|---|---|
| Título | "Minha trajetória no Ifes" |
| Nome | Só se fornecido; como a fonte informa; quebra de linha, nunca truncado |
| Formações | Até 4, **tantas quantas couberem** na área segura com o corpo mínimo (composição adaptativa): curso em destaque; "unidade · nível · modalidade · ano" (só os presentes), quebrado só entre atributos |
| Excedente | "e mais N formações registradas" para todas as não exibidas |
| Derivado | "N formações registradas no Ifes" |
| Agregados (P2) | No máximo **um par** (`agregado_curso` e `agregado_unidade` + apuração): o da primeira formação, na ordem de exibição, com agregado selecionado, **só se couber** depois das formações (FR-033). Sujeitos ao DP-2105 |
| Rodapé | `card_rodape` ("Instituto Federal do Espírito Santo"); na demonstração, `card_demo`. Ambos ancorados na base da área segura |

## Conteúdo vedado (FR-035, FR-036)

O card não pode conter:

- forma de oferta, data completa, tempo decorrido ou ingresso;
- Resposta ou qualquer dado declarado;
- CPF, data de nascimento ou contato;
- brasão, selo, assinatura institucional, QR ou identificador;
- número ou data de emissão;
- "certificado", "comprovante" ou "declaração".

## Garantias técnicas

- **SVG:**
  - mesma entrada, mesmos bytes;
  - `<title>` e `<desc>` textuais (FR-067);
  - `font-family="Open Sans, system-ui, sans-serif"`.
- **PNG:**
  - rasterizado do mesmo SVG com Open Sans Regular e Bold embutidas e sem as fontes do
    sistema;
  - 1080 × 1920;
  - reprodutível no mesmo ambiente.
  - Na indisponibilidade, `png_de` devolve `None` e a página cai para o SVG.
- **Entrega:**
  - PNG `inline` com nome `minha-trajetoria-ifes.png` (abre como imagem, salvável);
  - download pelo atributo `download`;
  - SVG `attachment`;
  - sem cache e nada guardado.

## Na página (FR-073)

- **Prévia:** `<img>` da própria PNG, com `alt`. Tocar e segurar salva a imagem no
  celular.
- **"Incluir meu nome no card":** um formulário GET que atualiza a prévia, sem
  JavaScript.
- **"Baixar imagem":** link com `download`.
- **"Compartilhar":** botão oculto por padrão. Só aparece com
  `navigator.canShare({files})`. Abre o menu de compartilhamento do sistema com o PNG; o
  sistema não envia nada a terceiros (FR-039). **Os destinos do menu dependem do
  dispositivo.** O Instagram pode não aparecer, e então o caminho é salvar e anexar.

## Temas (P3, FR-065)

- Um tema é só um conjunto de tokens (cores, grafismos das faixas) sobre o mesmo template
  e a mesma área segura.
- O texto é idêntico entre temas.
