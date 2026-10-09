# Validação — Feature 028, direção B

**Data:** 2026-10-09. Só demonstração, com personas fictícias.
**Branch:** `codex/028-camada-visual-portal`.

## Ambiente e linha de base

Guia `docs/desenvolvimento/ambiente-local.md`: uv 0.11.21, Python 3.13.14,
Django 5.2.17, PostgreSQL 16.14, dependências sincronizadas com `--extra dev --locked`.
Banco novo `trajetoria_028` e quatro chaves novas no `.env` ignorado pelo Git; nenhum
banco já preparado foi recriado. Preparo e servidor usam as mesmas chaves.

**Desvio operacional registrado:** a porta 8000 já estava ocupada pelo servidor da
worktree de auditoria. O processo existente foi preservado. A validação desta branch
usa `127.0.0.1:8028`; envio por Lote não é exercitado (a regra de 8000 da 020 permanece).

Antes de alterar a aplicação: ruff, check e makemigrations passaram; suíte com
**3245 passed, 40 skipped, 2 deselected**, em **276,99 s**. Os 40 skips são de vídeo,
sem o renderizador Node instalado nesta worktree. O teste de acesso com dados fictícios
foi conferido por HTTP e no navegador; nenhuma credencial real é usada.

## Regressões e verificações

- Novas regressões da 028 primeiro falharam contra a aplicação anterior: seis falhas
  sobre página pública, base, painel, prévia e escolha fixa do template.
- Recorte final: **719 passed**, em **16,23 s**, cobrindo Portal, narrativa, entradas e
  demonstração. Shell de referência, Portal desligado, fronteiras e ausência de escritas
  indevidas passaram. A referência de shell não foi editada.
- Testes antigos de raiz sem sessão foram revisados para a página pública especificada.
- Regressões da legenda cobrem imagem genérica, própria e unidade de outra formação.
  Os hashes históricos do agrupamento em zonas foram preservados: o teste recompõe só
  a legenda anterior para continuar provando o agrupamento contra os hashes originais.
  Os testes editoriais verificam a legenda corrigida normalmente. A suíte completa
  identificou também uma expectativa antiga da legenda no teste de composição do vídeo;
  essa expectativa foi atualizada para “Ifes · ilustração”, conforme a ADR.
- `ruff check .`: passou. `manage.py check`: sem problemas.
  `makemigrations --check --dry-run`: nenhuma mudança.
- Suíte completa final: **3254 passed, 40 skipped, 2 deselected**, em **380,20 s**.
  Nenhuma falha. Os skips de vídeo mantêm a limitação de ambiente registrada na linha
  de base; os dois testes desmarcados seguem a configuração da suíte.

## Evidência visual

[Comparação lado a lado](evidencias/index.html),
[medidas](evidencias/medidas.json) e [contraste](evidencias/contraste.json).

O script [verificar_visual.py](verificar_visual.py) confirma a identificação por HTTP,
baixa o HTML realmente servido e suas imagens, mede e captura snapshots temporários
no Chrome local. Nenhuma página de protótipo é usada como substituta da aplicação.
A moldura tem largura exata, inclusive abaixo do mínimo da janela headless; fonte
ampliada significa 200% no elemento raiz. Os snapshots e tokens CSRF não são versionados. Os scripts da aplicação são removidos
dos snapshots; somente a moldura executa JavaScript de medição. A trajetória também foi
remedida isoladamente sem seu script opcional de compartilhamento.

Matriz: página pública, entrada, Início de Ana e Diego, trajetória, contato,
oportunidades e instrumento como referência; 320/375/768/1024/1280/1440 px,
fontes 100% e 200%, além das primeiras telas.

### Primeira tela

No celular, as coordenadas incluem a faixa de demonstração, como na 024. No desktop,
subtrai-se a altura da faixa, como manda a ADR 0009. As capturas `*1280x720.png` e
`*1440x900.png` mostram a área de produto já com a faixa descontada.

| Persona | Título a 375×812 (fim) | Primeiro fato a 375×812 (fim) | Prévia/ação a 1280×720 (início, descontada a faixa) |
|---|---:|---:|---:|
| Ana | 367 px | 555,4 px | 657,2 px |
| Diego | 367 px | 555,4 px | 600 px |

Ambas passam; a 1440×900 também. O achado da Ana no protótipo foi resolvido com
espaçamento menor no reconhecimento e na seção de ações no desktop, preservando
agregados, frases e proveniência. A página pública mostra proposta e ação de entrar
na primeira tela a 1280×720.

Container útil: **1088 px** a 1280 e 1440. Duas colunas na seção de ações a 1024/1280/1440;
uma a 320/375. Linha do tempo do Diego horizontal no desktop e vertical no celular.
Nenhuma rolagem horizontal nas telas harmonizadas, nas duas fontes.
O destaque de Oportunidades mede **218,6 px** a 375 com ambas as personas, abaixo dos
270 px, com título, explicação, unidade responsável, origem e domínio preservados.

A verificação de alvos cobre links de conteúdo/navegação, botões, `summary` e rótulo
clicável da opção de nome no card. Campos de texto conservam a altura mínima da 015.
O instrumento é uma referência preservada: seu link de trajetória já tinha um alvo
menor no layout original; ele fica registrado nas medidas e não é modificado pela 028.

Contrastes de texto da camada: todos ≥ 4,5:1. Os menores registrados são 6,03:1
(texto suave sobre creme) e 6,16:1 (texto suave sobre tonal). Branco sobre a faixa:
12,59:1; ação verde sobre branco: 9,34:1.

### Conferência no navegador

No Chrome conectado: navegação por Tab, foco visível no salto para o conteúdo,
entrada por Enter, abertura do painel fictício por Enter e identificação da Ana pelo
controle fictício. A 375×812, primeiro fato visível, sem rolagem horizontal.
A 1280×720, prévia/ação da Ana confirmada em 657,2 px na área útil.

A ação “Pesquisa” abre `/formacoes/` com `--cor-acao: #1351b4` e sem tokens da camada
visual do Portal. Navegação e painel usam HTML nativo; renderização medida sem execução
de scripts da aplicação. O compartilhamento opcional da 021 permanece progressivo.

### Diferenças em relação ao protótipo escolhido

- Marca e faixa de demonstração reais da 015, com textos completos e assinatura intacta.
- Espaçamento do desktop corrigido para a primeira tela da Ana.
- Textos, atributos e anos derivados vêm do contrato da narrativa, sem dados copiados
  dos scripts dos protótipos. A prévia é o SVG do endpoint já existente da própria Pessoa.
- Nome fictício aparece só na faixa; o card do Início não inclui o nome.
- Contato público descreve a finalidade existente: convite para pesquisas, opcional.
- Harmonização das telas que estavam fora dos nove protótipos, sem mudar seus fluxos.

## Correções do code review (2026-10-09)

Revisão da branch contra a ADR 0009: as dez decisões foram atendidas. Seis problemas
menores foram corrigidos, sem mudar regra nem fluxo:

1. **Ação do card repetida no Início.** "Baixar o card da sua trajetória" aparecia junto
   da prévia e de novo na lista de ações. Com a prévia, a ação fica só junto dela.
2. **Proteção da 025 apontava para folha morta.** O teste que impede o CSS de esconder
   título, explicação e origem das oportunidades lia `portal/inicio.css`, que deixou de ser
   incluído. Agora lê `visual.css`; `inicio.css` foi removido.
3. **Prévia do card no formato da Minha trajetória.** O Início usava sempre o SVG, que
   depende da fonte do aparelho. Agora usa o PNG, com as fontes embutidas, quando há
   rasterização, como a 021; o SVG fica para quando não há.
4. **Card de exemplo gerado, não copiado.** `portal/exemplo.svg` era uma cópia de um card
   gerado. Agora `portal/exemplo.py` gera o exemplo com o código da 021 a partir de
   formações fictícias, sem banco. O resultado é idêntico, byte a byte, à cópia removida.
5. **Alvos de 44 px só nas ligações isoladas.** A regra `main a` transformava em caixa
   também a ligação no meio de um texto ("Conferir os dados" em `/entrar/`). Agora vale
   para itens de lista e parágrafos de uma ligação só (classe neutra `ligacao-isolada`,
   porque o template de acesso é núcleo). A verificação visual passou a ignorar ligações
   em linha, como a exceção da WCAG 2.5.8.
6. **Menores.** `imagens.legenda()` perdeu o parâmetro `unidade`, sem uso desde a correção
   da legenda (o teste de zonas reproduz a legenda histórica pela unidade do caso). O card
   de exemplo ganhou contorno, porque seu pé escuro sumia na faixa da mesma cor.

`verificar_visual.py` agora falha se um trecho que ele adapta no `medir.py` dos
protótipos não existir, em vez de medir outra coisa em silêncio, e aceita `--base`.

**Verificações:** ruff, check e makemigrations passaram. Suíte completa: **3257 passed,
40 skipped, 2 deselected**, em **288,92 s**, com `PGDATABASE=trajetoria_revisao_028b`.
Remedição visual com servidor do código corrigido em `127.0.0.1:8029`, mesmo banco e
chaves da demonstração da 028: **nenhuma falha**. Primeira tela inalterada: prévia/ação a
657,2 px (Ana) e 600 px (Diego) a 1280×720; primeiro fato a 555,4 px a 375×812; destaque
de Oportunidades com 218,6 px a 375.

## Limites e próximos passos

As capturas e medições não substituem teste com egressos. O Checkpoint 1 continua
**NÃO APLICADO**. Fotografias licenciadas, identidade definitiva, linguagem/nome
institucionais e uso real continuam com as pendências da ADR 0009.

Entrega local revisável, sem publicação ou merge da implementação. O próximo passo é
revisar a comparação visual e abrir o PR da 028; depois aplicar o Checkpoint 1 na
experiência executável. 026 e 027 permanecem fora do avanço atual.

### Incidente de validação resolvido

Dois recortes de pytest foram iniciados no mesmo banco de teste por engano. A execução
concorrente foi interrompida; a rodada completa final usa exclusivamente
`PGDATABASE=trajetoria_028_verificacao`. O banco de demonstração não foi alterado por
esse incidente. Resultados de execuções com colisão não são contados como verificação.
