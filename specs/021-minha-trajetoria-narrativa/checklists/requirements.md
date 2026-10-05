# Specification Quality Checklist: Minha Trajetória — narrativa visual personalizada

**Purpose**: Validar completude e qualidade da especificação antes do planejamento.

**Created**: 2026-10-04

**Feature**: [spec.md](../spec.md)

**Marker Semantics**: `[x]` significa requisito revisado quanto à qualidade. Não significa
implementação, teste executado nem aprovação institucional.

## Content Quality

- [x] Sem desenho de implementação: models, rotas, nomes de campo, biblioteca de
  rasterização, dimensões do card e mecanismo de carga ficam para o plan.
  - "SVG" e "PNG" aparecem porque são o formato do artefato pedido pelo solicitante, não
    escolha de tecnologia.
  - `CAMPOS_DE_CONTEXTO`, snapshot e colunas da 013 aparecem como invariantes de features
    existentes a proteger, não como desenho novo.
- [x] Foco no valor para o egresso (reconhecimento, devolutiva) e para a instituição
  (credibilidade, nenhum fato inventado, pesquisa intacta).
- [x] Texto compreensível para responsáveis pelo produto. O catálogo de formulações e a
  lista de formulações vedadas estão em linguagem natural.
- [x] Todas as seções obrigatórias do template ativo preenchidas, inclusive Origem dos
  Dados, Invariantes, Fronteira do NIAE e Decisões Pendentes.

## Requirement Completeness

- [x] Nenhum marcador [NEEDS CLARIFICATION].
  - As escolhas reversíveis estão em E1 a E7 e podem ser revistas no `/speckit-clarify`.
  - As regras institucionais estão em DP-2101 a DP-2109.
- [x] Requisitos testáveis e inequívocos: 73 FRs (FR-070 a FR-073 acrescentados no
  clarify e na revisão do plan) e uma matriz de verificação automatizada.
- [x] Critérios de sucesso mensuráveis: 14 SCs.
- [x] Critérios de sucesso descrevem resultados observáveis, sem tecnologia.
- [x] Cenários de aceitação definidos nas sete histórias: quatro P1, duas P2 e uma P3.
- [x] Bordas identificadas:
  - várias Participações;
  - mesmo curso e ano;
  - vocabulário da fonte;
  - data de referência inconsistente;
  - nome longo;
  - muitas formações no card;
  - agregado = 1 ou sem apuração;
  - fonte indisponível;
  - Pessoa não incorporada;
  - Campanha encerrada.
- [x] Escopo delimitado em Out of Scope. Sem vídeo, dados declarados, marcos, fotos, IA,
  página pública, editor de privacidade nem métricas extras.
- [x] Dependências e suposições identificadas: sessão da 018, demonstração, data de
  referência, dependência de rasterização justificada no plan, 001/DP-006.

## Feature Readiness

- [x] Todo FR tem critério verificável, por cenário de aceitação ou pela matriz.
- [x] As histórias cobrem os fluxos principais: ver, honestidade, baixar, não
  interferência, ingresso, agregados, tema.
- [x] P1 é entregável sozinho, sem migração. P2 é aditivo e testável de forma
  independente. P3 é opcional.
- [x] Nenhum detalhe de implementação vaza para a spec além dos invariantes existentes
  citados.

## Constitution alignment (projeto)

- [x] Princípio III: cada elemento com origem; derivados não gravados; Respostas não
  usadas.
- [x] Princípio V: o adaptador separa a linha larga; o contrato expõe conceitos.
- [x] Princípio XVI: subconjunto compartilhável conservador, nome por escolha, nada
  persistido, sem link público.
- [x] Princípio XXII: narrativa não persistida, duas métricas fechadas, um tema em P1,
  vídeo em feature separada.
- [x] Princípio XXIX: regras institucionais (compartilhamento, marca, nome social,
  ingresso real, agregados reais, imagens, Versões, Portal) como DECISÃO PENDENTE.
- [x] Revisões em features anteriores listadas: 014 FR-041, 001 FR-012 (P2), nota na 018,
  esclarecimento da auditoria de 2026-10-02 §5.

## Notes

- Validação feita em uma iteração. Correção aplicada durante a revisão: as frases usavam
  "Campus Serra". A fonte informa "Serra" e as unidades incluem Cefor e campus avançado. O
  FR-017 agora veda acrescentar "Campus", e as formulações usam "na unidade {unidade}".
- Clarify de 2026-10-04: oito decisões do solicitante integradas (seção Clarifications).
  - Grão é a Pessoa; a Participação concluída é gatilho.
  - Narrativa derivada na consulta.
  - Justificativa do ingresso corrigida.
  - Agregados contam Conclusões, com linguagem vedada ampliada.
  - Apuração só quando única (DP-2109).
  - Nome desmarcado e card sem nome.
  - Antecipação do benefício (FR-070).
  - Privado × compartilhável.

  Corrigido também: FR-033 citava DP-2104 para agregados; o certo é DP-2105.
- Revisão do plan (2026-10-04), duas mudanças pedidas pelo solicitante:
  - P2 por capacidade separada da `FonteAcademica` (E5a, FR-071, SC-014). Identidade e
    incorporação nunca dependem do enriquecimento.
  - Card focado em rede social vertical: 9:16 com área segura, PNG como artefato principal,
    prévia salvável e compartilhamento nativo como melhoria progressiva (E6, FR-031,
    FR-040, FR-072, FR-073, SC-013).
- Itens do plan:
  - escolha da rasterização e da fonte embutida (Complexity Tracking);
  - dimensões do card e limite de formações exibidas;
  - forma da operação de agregados na fronteira;
  - momento da carga.
