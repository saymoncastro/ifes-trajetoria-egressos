# Quickstart — validar a Feature 022

Roteiro de validação. Os detalhes estão em [plan.md](plan.md), [rotas](contracts/rotas.md),
[composição visual](contracts/composicao-visual.md), [renderizador](contracts/renderizador.md),
[template](contracts/template-video.md) e [data-model](data-model.md). Todos os dados são
fictícios.

## Pré-requisitos

- **Ambiente base:** o mesmo da [021/quickstart](../021-minha-trajetoria-narrativa/quickstart.md),
  com Python 3.13, uv, PostgreSQL local, as chaves da 018 e da 019.
- **Node ≥ 22:**

```bash
node --version
```

Instale o projeto de vídeo e provisione o navegador. Ocupa ~600 MB e é feito uma vez. O
navegador precisa ser provisionado pelo script npm, que roda dentro de `video/` (o Remotion
resolve o diretório pelo diretório atual):

```bash
npm ci --prefix video
```

```bash
npm --prefix video run garantir-navegador
```

Use um banco novo e isolado:

```bash
createdb trajetoria_demo_022
```

```bash
uv sync --extra dev && PGDATABASE=trajetoria_demo_022 uv run python manage.py migrate
```

```bash
PGDATABASE=trajetoria_demo_022 TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py preparar_demonstracao
```

Dois terminais: o servidor e o processador de vídeos.

```bash
PGDATABASE=trajetoria_demo_022 TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py runserver 127.0.0.1:8000
```

```bash
PGDATABASE=trajetoria_demo_022 TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py processar_videos
```

## Verificação automática

```bash
uv run pytest tests/video tests/narrativa
```

Esperado:

- **Sem `video/node_modules`:** os testes de mídia aparecem como *skipped*, com o motivo.
- **Com o renderizador:** todos rodam: MP4, `ffprobe` e quadros-chave (research R14).

Teste de regressão do card (o SVG não pode mudar com o agrupamento por zonas):

```bash
uv run pytest tests/narrativa/test_card.py tests/narrativa/test_card_editorial.py
```

## Cenários manuais

Entre em `http://127.0.0.1:8000/acesso/` com uma Pessoa fictícia que tenha Participação
concluída (lista no `preparar_demonstracao`). Depois abra `/minha-trajetoria/`.

| # | Ação | Esperado | Referência |
|---|---|---|---|
| 1 | Abrir a página | Card como na 021; bloco "Vídeo da sua trajetória" com "Gerar vídeo". Nenhum vídeo gerado | FR-002, FR-034 |
| 2 | Gerar vídeo | Volta à página com "Estamos preparando seu vídeo…"; o restante funciona | FR-031, FR-034 |
| 3 | Aguardar segundos e atualizar | Prévia do vídeo com pôster do card, sem autoplay; "Baixar vídeo (MP4)" | FR-034, FR-036 |
| 4 | Reproduzir | ~8 s: abertura, título, linha do tempo, destaques, fecho; termina parado no card; rodapé de demonstração o tempo todo | FR-011 a FR-015 |
| 5 | Baixar | Arquivo `minha-trajetoria-ifes.mp4` | FR-026 |
| 6 | Marcar "Incluir meu nome" e gerar | Novo vídeo, com o nome; o vídeo sem nome continua disponível pela outra escolha | FR-021 |
| 7 | Gerar de novo a mesma escolha | Pronto na hora, sem nova geração (o processador não registra trabalho) | FR-032, SC-006 |
| 8 | Parar o processador e gerar outra escolha | "Preparando…"; depois de 10 min (a limpeza marca `sem_processador` e apaga a composição), "Não foi possível preparar o vídeo agora" e "Tentar novamente"; card intacto | FR-034, R7 |
| 9 | Sem JavaScript, repetir 2 a 5 | Tudo funciona por recarga | FR-035 |
| 10 | Renomear `video/node_modules` e reiniciar o servidor | Página sem o bloco de vídeo, idêntica à 021 | FR-037 |
| 11 | No celular (iPhone e Android), abrir a prévia e compartilhar | Reproduz inline; o menu do sistema recebe o MP4; publicar como story de teste | SC-008 |
| 12 | Só com teclado (Tab, Enter, Espaço), em janela de 320 px de largura: gerar, atualizar, reproduzir, baixar e tentar de novo | Todos os controles alcançáveis, com foco visível; sem rolagem horizontal; leitor de tela anuncia a mudança de estado | FR-036, SC-007 |

## Inspecionar um MP4

```bash
npx --prefix video remotion ffprobe -v error -show_entries stream=codec_name,pix_fmt,color_space,width,height,r_frame_rate:format=duration -of compact minha-trajetoria-ifes.mp4
```

Esperado: `h264`, `yuv420p`, `bt709`, 1080 × 1920, `30/1`, duração 8,0 s (8,6 s com 4
formações) e **uma única** linha de `stream`, sem áudio.

## Referências visuais

Gere os quadros-chave e os MP4 dos casos de referência para a aprovação do solicitante
(SC-008):

```bash
uv run python specs/022-minha-trajetoria-video/evidencias/gerar_referencias.py
```

O script avulso é criado na implementação, como o da 021.
