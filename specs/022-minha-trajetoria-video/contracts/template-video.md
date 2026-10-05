# Contrato: template de vídeo `trajetoria-v1`

FR-009 a FR-017 e FR-019; research R10. O template **só** decide tempo e movimento das
partes da [ComposicaoVisual](composicao-visual.md). Ele não tem dado, texto nem regra
própria.

## Quadro

| Item | Valor |
|---|---|
| Dimensões | 1080 × 1920, fundo opaco creme do tema |
| Taxa | 30 fps |
| Duração | **240 quadros (8,0 s)** com até 3 nós; **258 quadros (8,6 s)** com 4 nós. O card exibe no máximo 4, então 8,6 s é o máximo (≤ 10 s do FR-010) |
| Áudio | Nenhum |

`extra` = 18 quadros (0,6 s) com 4 nós; 0 nos demais casos.

## Linha do tempo das zonas

| Zona | Entrada (quadros) | Movimento |
|---|---|---|
| `fundo`, `rodape` | Visíveis do quadro 0 ao último | Nenhum (FR-015) |
| `abertura` | 0 → 21 | Opacidade 0 → 1; **escala da imagem** 1,04 → 1,00 até o quadro 39, com origem no centro superior. Texto não escala |
| `marca` | 4 → 21 | Opacidade |
| `legenda` | 9 → 21 | Opacidade e translação +12 → 0 px |
| `titulo` | 21 → 39 | Opacidade e translação +24 → 0 px |
| `nome` | 33 → 51 | Idem |
| `traco` | 51 → início do último nó | Revelação de cima para baixo (recorte), trecho a trecho: do centro do nó *i* ao do nó *i + 1* (`paradas`) entre o início do nó *i* e o do nó *i + 1*; chega a cada nó quando ele começa a entrar |
| `nos[i]` | 51 + i·p → +min(p, 18) | Opacidade e translação +24 → 0 px. `p` = (150 + extra − 51) / (nº de nós + 1 se houver `mais`) |
| `mais` | Depois do último nó, mesma duração | Idem |
| `destaques[i]` | 150 + extra + 8i → +18 | Opacidade e translação +24 → 0 px. **Número estático, sem contagem** |
| `apuracao` | Com o primeiro destaque | Opacidade |
| `fechamento` | 189 + extra → 207 + extra | **Só opacidade**: o rodapé visível está logo abaixo |
| (repouso) | 207 + extra → último | **Nenhum movimento**: ≥ 33 quadros (1,1 s) iguais ao card (FR-014) |

Sem destaques, as janelas de destaques e apuração ficam vazias. O vídeo mantém 8,0 s, e o
tempo vira permanência (FR-013).

Com 4 nós, só a janela da linha do tempo se alonga (`extra`). As fronteiras seguintes se
deslocam pelo mesmo `extra`, e destaques e fechamento mantêm suas durações (spec FR-011,
revisão do analyze I1).

**Toda zona é opcional para o template:** zona ausente não é desenhada. Uma parte com
marcação vazia ocupa sua vaga no tempo sem desenhar nada. Isso permite os renders reduzidos
usados como máscara nos testes de quadro (tasks T022), que mantêm o número de nós e, com
ele, o tempo e a duração.

## Regras de movimento

- *Easing* único: `bezier(0.22, 1, 0.36, 1)`, com *clamp* nas duas pontas.
- **Translação só de baixo para cima e ≤ 24 px.** O texto em movimento só alcança a área da
  zona seguinte, que ainda está invisível. Nenhum texto visível é coberto (FR-017).
- Permitido: opacidade, translação, escala da imagem e revelação do traço (FR-016).
- Vedado: partículas, 3D, câmera, física (`spring`), filtros, desfoque e contadores.
- Nenhuma parte sai da área segura em posição final. Em movimento, o deslocamento máximo é
  de 24 px para baixo da posição final. Como o fechamento não se move, o último texto em
  movimento fica a pelo menos 40 px (`ESPACO_FECHO`) do fechamento.

## Fontes

Open Sans Regular e Bold, carregadas por `FontFace` antes do primeiro quadro
(`delayRender`). Sem a fonte, o render falha (código 1), sem cair para fonte do sistema.

## Versão

Mudança perceptível de tempo, movimento ou duração → `trajetoria-v2` (FR-019).
