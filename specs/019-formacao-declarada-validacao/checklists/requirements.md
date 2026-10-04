# Specification Quality Checklist: Formação não localizada e validação posterior

**Purpose**: Validar completude e qualidade da especificação antes do planejamento.

**Created**: 2026-10-04

**Feature**: [spec.md](../spec.md)

**Marker Semantics**: `[x]` significa requisito revisado quanto à qualidade. Não significa
implementação, teste executado nem aprovação institucional.

## Content Quality

- [x] Sem desenho de implementação. Modelo físico, rotas, nomes de coluna, mecanismo de
  sessão e forma de serialização ficam para o plan.
  - HMAC e chaves da 018 aparecem porque são decisão fechada da 018.
  - A criptografia reversível dos dados para consulta ao acervo aparece porque é decisão
    do solicitante (decisão 10). Algoritmo, formato e custódia da chave ficam para o plan
    e para DP-1903.
  - A "fonte de acervo histórico" é conceito de domínio (M1+), não escolha técnica.
- [x] Foco no valor para o egresso (responder sem estar na base digital) e para a
  instituição (dados oficiais não contaminados, proveniência).
- [x] Texto compreensível para responsáveis pelo produto.
- [x] Todas as seções obrigatórias do template ativo preenchidas, inclusive Invariantes,
  Fronteira do NIAE e Decisões Pendentes.

## Requirement Completeness

- [x] Nenhum marcador [NEEDS CLARIFICATION]. As escolhas reversíveis estão em E1 a E9 e
  podem ser revistas no `/speckit-clarify`. As regras institucionais estão em DP-1901 a
  DP-1912.
- [x] Requisitos testáveis e inequívocos: 68 FRs, depois da revisão de sanidade (eram 92), e
  uma matriz de verificação.
- [x] Critérios de sucesso mensuráveis: 11 SCs.
- [x] Critérios de sucesso descrevem resultados observáveis, sem tecnologia.
- [x] Cenários de aceitação definidos nas oito histórias.
- [x] Bordas identificadas:
  - par que passa a confirmar;
  - formações duplicadas ou múltiplas;
  - recusa do termo;
  - rascunho com Campanha encerrada;
  - validação depois do snapshot;
  - concorrências;
  - Conclusão sem unidade;
  - unidade divergente no acervo;
  - colisão de CPF;
  - fonte indisponível.
- [x] Escopo delimitado em Out of Scope: sem notificação, reabertura, resolução de
  conflito, fusão de Pessoa, cadastro manual, workflow ou nova Versão.
- [x] Dependências e suposições identificadas:
  - **emenda constitucional como pré-requisito** (DP-1912 bloqueia o plan);
  - demonstração apenas;
  - baseline 2024 transitória.

## Feature Readiness

- [x] Todos os FRs têm verificação nas histórias, na matriz ou nos SCs.
- [x] As histórias cobrem declaração, quarentena, validação pela fonte digital,
  validação pelo acervo, não confirmação, fora da abrangência, conflito, abrangência
  provisória, retomada e acompanhamento.
- [x] Os resultados permitem demonstrar o ciclo completo com dados fictícios.
- [x] Nenhuma solução técnica antecipada além das decisões fechadas do solicitante.

## Notes

- **Base.** `main` em `2f1ee86`, depois da 018.
- **Lido.** Constituição 1.0.0; 001 a 013, 017 e 018; ADR 0004; auditoria de identidade
  com o adendo; inventário 2024.
- **Auditoria própria.** [2026-10-04-formacao-declarada-validacao](../../../docs/auditorias/2026-10-04-formacao-declarada-validacao.md),
  revisada com as decisões do solicitante: B′, M1+ e abrangência provisória e definitiva.
- **Pré-requisito.** Aprovar o diff constitucional (auditoria §11) e decidir a
  classificação (DP-1912) antes do `/speckit-plan`.
- **Revisão de 2026-10-04.** Trocou "só HMAC" por HMAC + criptografia reversível dos dados
  para consulta ao acervo (FR-014, FR-076, FR-110, FR-114 a FR-119). Saiu a conferência
  por HMAC, que ficou sem consumidor.
- **Revisão de 2026-10-04 (ajustes do solicitante).**
  - Persistência só ao criar a declaração (FR-002, FR-016).
  - HMAC do CPF para agrupamento e HMAC do par só para retomada (FR-014).
  - "Não reexibidos após a captura" (FR-110).
  - Dados para consulta ao acervo como conjunto próprio, anterior à decisão (FR-114).
  - E1 confirmada.
- **Para o `/speckit-clarify`, se quiser rever.** E3 (escopo da CSAEG), E4 (regra do
  conflito), E7 (critério não coletado na compatibilidade provisória) e E8 (retomada pelo
  par).

## Revisão de sanidade dos requisitos

Feita em 2026-10-04, antes do plan. Critério: tirar repetição e requisito puramente
derivado, sem remover controle substantivo. A numeração original foi preservada, com
lacunas.

### Classificação dos 68 requisitos

| Grupo | Requisitos | Qtd. |
| --- | --- | --- |
| Núcleo funcional | FR-001, 005, 006, 010–013, 015, 016, 020–024, 030, 032, 033, 036, 040, 042, 043, 050, 051, 061, 063–065, 070, 073, 074, 077, 080–084, 090, 092, 093 | 39 |
| Segurança e privacidade | FR-002, 003, 014, 076, 110, 111, 113–117, 119 | 12 |
| Integração e efeitos em features anteriores | FR-004, 100–104, 106, 120, 121, 130–132 | 12 |
| Decisões pendentes e operação | FR-060 (DP-1902), 062 (DP-1901), 071 (DP-1904), 072 (DP-1905), 118 (DP-1903) | 5 |

### Consolidados (lacunas na numeração)

| Antigo | Destino | Motivo |
| --- | --- | --- |
| FR-025 | FR-020 | Mesma regra de mobilização |
| FR-031 | FR-030 | Cardinalidade da âncora |
| FR-034, FR-035 | FR-033 | Mensagem final; "não exibir Respostas" já é regra da 008 |
| FR-041 | FR-040 | Regras da sessão da 018 |
| FR-044 | FR-006 | "Declarante não vê resultado" |
| FR-052, FR-053, FR-079 | FR-051 | Conclusão efetiva e preservação dos não oficiais |
| FR-066 | FR-060 | "Só dados fictícios" já decorre de FR-130 e de DP-1902 |
| FR-067 | FR-061 + Out of Scope | A proibição de workflow é escopo, não comportamento |
| FR-075 | FR-070 | Confirmação antes de gravar |
| FR-078 | FR-015 | Validação não altera nada |
| FR-085 | FR-081 | Imutabilidade da Referência |
| FR-086, FR-087 | FR-080 | Cadastro manual vedado; tratamento igual a qualquer Conclusão |
| FR-091, FR-094 | FR-090 | Conflito num só requisito |
| FR-105 | FR-102 | Decorre do universo |
| FR-107 | FR-106 | Proibições da exportação junto da coluna |
| FR-108 | — | Herdado da 013 FR-013 sem mudança |
| FR-112 | FR-071, FR-110 | Operador na decisão; logs sem dados pessoais |
| FR-122 | FR-010, FR-011 | Repetia os cinco campos |
| FR-133 | FR-132 | Operadores fictícios junto dos cenários |

### Simplificações de substância

- **FR-101.** De cinco contadores no acompanhamento (aguardando, não confirmadas, fora da
  abrangência, em conflito, mais o link) para **um** indicador ("Validações de formação: N
  na fila"). O detalhe por situação fica na própria fila. É o que o solicitante descreveu.
- **FR-010.** Sai "curso com sugestões". O campo é texto simples; sugestão seria catálogo
  sem fonte (inventário O-14).

### Avaliados e mantidos de propósito

| Item | Por que fica |
| --- | --- |
| Retomada pelo par (FR-043, US7) | A sessão expira em 30 min de inatividade, e o instrumento 2024 tem 54 perguntas. Sem retomada, o egresso que mais precisamos alcançar recomeça do zero e gera declaração duplicada |
| Agrupamento pelo HMAC do CPF (FR-065) | Custo baixo, sobre um HMAC que já existe. É o que torna visível a duplicidade causada por data diferente |
| Congelar a Participação no snapshot (FR-104) | Sem isso, uma validação posterior muda a leitura de snapshot antigo, o que viola a 012 FR-050 |
| Origem da formação com três valores (FR-106) | Distinguir fonte digital de acervo é a proveniência pedida pelo solicitante |
| Situação analítica com seis valores (FR-050) | Cada valor tem efeito distinto, e todos são derivados: nenhum é estado armazenado nem workflow |

### Para o plan (não é requisito)

- **Identificador da chave de criptografia.** Guardar, junto dos dados para consulta ao
  acervo, um identificador da versão da chave com que foram cifrados. É um campo barato
  que permite rotação futura sem adivinhação. O **procedimento** de rotação fica fora da
  019 (DP-1903).
- **Algoritmo e formato da criptografia.** Escolha do plan, com criptografia autenticada.
