# ADR 0003 — Q14 permanece Resposta declarada, mesmo divergente da formação

- **Status**: Aceito. Decidido pelo solicitante em 2026-10-01, a partir do achado D-2 da
  auditoria de UX da Feature 008.
- **Data**: 2026-10-01
- **Contexto de origem**: [auditoria de UX da Feature 008, D-2](../auditorias/2026-10-01-ux-feature-008.md#5-questões-de-domínio-descobertas),
  [spec da Feature 003, Q14 e DP-307](../../specs/003-migracao-semantica-instrumento/spec.md),
  [spec da Feature 008, FR-028](../../specs/008-interface-navegavel-pesquisa/spec.md),
  [inventário do formulário 2024, O-13](../referencias/formulario-egresso-ifes-2024-inventario.md)

## Contexto

Q14 ("Indique o questionário que pretende preencher") pergunta o nível da formação e
decide o ramo de cursos (S4 a S7). Desde a 007, toda Participação é vinculada a uma
Conclusão Acadêmica, cujo nível é exibido como contexto na própria tela ("Sobre a sua
formação").

A auditoria mostrou que as duas informações podem divergir sem nenhum sinal: uma egressa
de formação de nível Técnico marcou "Pós-Graduação" em Q14 e seguiu para a Seção
"Pós-Graduação" (78 cursos), com "Nível: Técnico" na mesma tela. A Participação passa a
conter respostas sobre um nível diferente do da Conclusão a que se refere.

O comportamento atual decorre de decisões vigentes:

- na 003, Q14 é candidata a contexto institucional, mas permanece na baseline como
  pergunta declarada até a DP-307 ser decidida (tratamento provisório);
- na 008, o contexto da formação não pode pré-preencher, sugerir, ocultar ou pular
  Perguntas, em particular Q10–Q19 (FR-028).

## Alternativas consideradas

- **Alertar sem bloquear** — a interface compararia Q14 com o nível da Conclusão e
  mostraria um aviso. Exige correspondência entre as Opções de Q14 e o vocabulário de
  nível da fonte acadêmica, ainda pendente (001/DP-007; DP-307), e uma regra nova na
  jornada.
- **Derivar Q14 da formação** — Q14 deixaria de ser perguntada e o ramo viria do nível da
  Conclusão. É exatamente o que a DP-307 ainda vai decidir, e revisaria o FR-028 da 008.
- **Manter como decisão pendente** — adiaria a resposta sem orientar quem analisa os
  dados.

## Decisão

**Q14 permanece Resposta declarada. A jornada não valida, não alerta e não deriva Q14 a
partir da Conclusão Acadêmica; a divergência entre o nível declarado e o nível
institucional é tratada na análise dos dados, não na coleta.**

Motivos:

- é o tratamento provisório já definido pela DP-307: todas as Perguntas acadêmicas na
  baseline, como declaradas;
- alerta ou derivação dependem de correspondência confiável entre as Opções do
  formulário e o vocabulário da fonte acadêmica, que ainda não existe;
- não exige mudança na interface (008), na jornada (006) nem no instrumento (003);
- a divergência fica preservada como dado: a Resposta de Q14 e a Conclusão da
  Participação continuam disponíveis para comparação.

## Consequências

- Uma Participação pode conter respostas de um ramo de cursos (S4 a S7) que não
  corresponde ao nível da sua Conclusão Acadêmica. Isso é comportamento aceito, não
  defeito.
- Análises, indicadores e exportações que usem o nível da formação DEVEM declarar a
  fonte: o nível institucional (Conclusão) ou o declarado (Q14). Quando as duas
  divergirem, a divergência deve ser identificável, nunca corrigida em silêncio.
- Nenhuma alteração de código decorre deste ADR.
- Este ADR não decide a DP-307. Reavaliar quando ela for decidida, ou antes, se a
  divergência se mostrar frequente na coleta.
