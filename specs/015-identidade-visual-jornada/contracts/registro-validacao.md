# Contrato: registro de validação (gate)

Arquivo (versionado): `specs/015-identidade-visual-jornada/validacao.md` — **só texto**.
Capturas **não versionadas**: anexadas ao PR da 015 ou mantidas como artefato externo,
cada uma com um identificador citado no registro, no formato
`R{rodada}-G{situação}-{A|B}-{largura}-{fonte}` (ex.: `R1-G2-B-375-200`).
Uma seção por **rodada**. A 015 só está pronta para merge quando uma rodada fecha com
todos os critérios objetivos aprovados (FR-042); rodada reprovada → correções na mesma
branch → nova rodada.

## Cabeçalho de cada rodada

- Data, commit medido, navegador e versão, Direção mergeada (B), valores de `--raio` e
  do divisor entre Perguntas medidos.
- Origem da assinatura: SVG oficial recebido (nome, origem, SHA-256) e forma de
  inclusão — ou "bloqueada por D-03" enquanto não houver SVG (research R3).

## Situações do gate (sempre as quatro)

| # | Situação | Pessoas / estado |
|---|---|---|
| G1 | Trajetória | Maria (seleção, duas formações) e Diego (outras formações, ambiguidade, já respondida); aviso `salvo` após "Salvar e sair" |
| G2 | Seção 8 "Avaliação" | 14 Perguntas, escalas, rádios, caixas, "Outro"; com Opções e pontos marcados |
| G3 | Seção 2 com pendências + Seção 8 com erro de forma | Envio parcial; descrição de "Outro" sem a Opção |
| G4 | "Concluir a pesquisa" → "Pesquisa concluída" | Fim da jornada |

## Medidas por situação

Larguras 375, 390, 430 e 1280 px; fonte a 100% e a 200%.

| Critério | Medida registrada | Limite |
|---|---|---|
| SC-001 | Assinatura na 1ª viewport a 375 px; altura do símbolo; área de proteção | Sim; ≥ 30 px; ≥ 1 módulo |
| SC-002 | Altura do cabeçalho (375/1280) e do rodapé (375) | ≤ 64 / ≤ 80 / ≤ 120 px |
| SC-003 | Contraste de cada par texto/fundo e de contornos/estados usados na tela | ≥ 4,5:1 / ≥ 3:1 |
| SC-004 | Foco visível em cada tipo de elemento focável, inclusive resumo focado ao carregar | Sim |
| SC-005 | Largura de rolagem = largura da janela | 320–1280 px, 100–200% |
| SC-006 | 014 SC-006 a SC-010 remedidos | Todos atendidos |
| SC-007 | Captura em escala de cinza de G3 (pendência × erro) | Distinguíveis |
| SC-008 | Espaço entre Perguntas; tamanho/peso do enunciado; auxiliar | 48 px; 18/600; 15 px suave |
| SC-009 | Opções e pontos marcados com estado visível; células delimitadas | 100% |
| SC-010 | Troca A↔B exclusivamente nos dois tokens de ação (`--cor-acao`, `--cor-acao-forte`) | Diff só nessas duas linhas |
| SC-011 | Inventário de onde o verde aparece | Só FR-004 |
| SC-012 | Capturas antes/depois: lista de Pesquisas, edição de Pergunta (009), painel de Campanha (011), 375 e 1280 px; prévia de Seção | 0 mudanças não intencionais; prévia é a única exceção deliberada (tipografia, estados e tratamento interno da Pergunta e dos controles — FR-040); shell, ritmo, espaçamento entre Perguntas e composição do editor inalterados |
| SC-013 | Suíte completa; ausência de JS, modelo, migração, recurso externo | Verde / 0 |

## Comparações

- **Direção A × B:** G1 a G4 a 375 e 1280 px nas duas direções, lado a lado (pares de
  identificadores de captura), com a tabela de contraste de cada uma.
- **Raio 0 × 4 px:** G2 e G3 a 375 px; valor escolhido e motivo.
- **Divisor entre Perguntas:** G2 a 375 px com e sem; decisão e motivo.
- **Ícones (opcional):** se avaliados, G1 e G4.

## Resultado

- Critérios objetivos: aprovado / reprovado (com lista do que falhou e da correção).
- **Revisão perceptiva** (não automatizada): pendente / realizada, com quem (ACS,
  CPAEG/Proex, egressos) e observações. Não bloqueia o fechamento (FR-043).
- Itens para a propagação futura (ex.: 403/404/500, shell administrativo).
