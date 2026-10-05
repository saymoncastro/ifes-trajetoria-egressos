# Specification Quality Checklist: Mobilização real, Lotes e contatos do egresso

**Purpose**: Validar completude e qualidade da especificação antes do planejamento.

**Created**: 2026-10-04 · **Revisado**: 2026-10-05, depois da atualização com a `main`
(021 e 022).

**Feature**: [spec.md](../spec.md)

**Marker Semantics**: `[x]` significa requisito revisado quanto à qualidade. Não significa
implementação, teste executado nem aprovação institucional.

## Content Quality

- [x] Sem desenho de implementação. Modelo físico, rotas, nomes de coluna, mecanismo de
  serialização da concorrência e limite por acionamento ficam para o plan.
  - POST/CSRF, TLS e "backend de e-mail" aparecem como requisitos de segurança e fronteira
    herdados da 016, no mesmo nível em que a 016 os especificou.
  - Os nomes de capacidade aparecem só no Input. Os FRs descrevem as três capacidades por
    ação.
- [x] Foco no valor: mobilizar sem disparo repetido, histórico reproduzível, egresso
  mantém o contato sem fricção.
- [x] Texto compreensível para responsáveis pelo produto.
- [x] Todas as seções obrigatórias do template ativo preenchidas, inclusive Invariantes,
  Fronteira do NIAE e Decisões Pendentes.

## Requirement Completeness

- [x] Nenhum marcador [NEEDS CLARIFICATION]. As escolhas E1 a E7 foram decididas pelo
  solicitante em 2026-10-05 (Clarifications): E1 e E7 confirmadas, E2 aceita só na
  demonstração com revisão antes do uso real (DP-2010), E3 a E6 mantidas. As regras institucionais estão em DP-2001 a DP-2009.
- [x] Requisitos testáveis e inequívocos: 46 FRs e uma matriz mínima de verificação.
- [x] Critérios de sucesso mensuráveis: 8 SCs.
- [x] Critérios de sucesso descrevem resultados observáveis, sem tecnologia.
- [x] Cenários de aceitação definidos nas sete histórias.
- [x] Bordas identificadas:
  - encerramento entre confirmação e envio;
  - divergência entre prévia e confirmação;
  - Lote vazio;
  - vários e-mails ou e-mail inválido;
  - e-mail igual ao importado;
  - interrupção depois do submit;
  - base incompatível com o modo;
  - Pessoa que sai da população.
- [x] Escopo delimitado em Out of Scope e nos Gates A e B.
- [x] Relação com 021 e 022 explícita: capacidade de contatos separada da fronteira
  acadêmica (precedente 021 FR-071); ação principal da conclusão preservada (021 FR-003
  revista só de "única" para "principal"); nenhum benefício depende de contato (021 FR-009,
  FR-070).
- [x] Dependências e suposições identificadas:
  - só demonstração;
  - sessão da 018;
  - adaptador real dependente do Gate A;
  - modo real dependente do Gate B.

## Feature Readiness

- [x] Todos os FRs têm verificação nas histórias, na matriz ou nos SCs.
- [x] As histórias cobrem:
  - preparação e congelamento;
  - envio e retomada;
  - duplicidade;
  - atualização pelo egresso;
  - reprodutibilidade;
  - importação;
  - governança.
- [x] Resultados mensuráveis cobrem duplicidade, reprodutibilidade, privacidade, bloqueio do
  modo real e não regressão da resposta espontânea.
- [x] Nenhum detalhe de implementação vaza além do herdado da 016.

## Constitution & YAGNI Review

- [x] **I, VII, VIII**: Lote não toca Participação; congelamento; snapshots intocados.
- [x] **II e ADR 0004**: Lote ⊆ abrangência, sem efeito em admissão (FR-017, FR-040,
  SC-007).
- [x] **III e IV**: origem e momento por registro, sem sobrescrita.
- [x] **V**: capacidade de contatos separada do contrato acadêmico (021 FR-071 como
  precedente) e fronteira de transporte.
- [x] **X**: preparar ≠ enviar; interpretação local reversível; DP-2001.
- [x] **XVI (NON-NEGOTIABLE)**: telefone excluído por falta de consumidor; nenhuma saída
  com contato; finalidade declarada.
- [x] **XXIX (NON-NEGOTIABLE)**: envio real desativado; base legal, remetente, retenção e
  opt-out como DP.
- [x] **XXII / YAGNI**, cortes explícitos:
  - rascunho persistido;
  - estado de Lote;
  - score ou "verificado";
  - criptografia por analogia;
  - telefone;
  - confirmação de e-mail;
  - fila e retry;
  - tracking;
  - editor;
  - lista de destinatários;
  - filtro por situação de contato;
  - conversão.
- [x] Pontos de complexidade mantidos e justificados:
  - `EM_TENTATIVA`/incerto: evita reenvio silencioso após falha de processo;
  - posição na ordem do adaptador: vários e-mails sem perda e sem escolha arbitrária;
  - operador registrado no Lote: rastreabilidade proporcional a ação de risco.

## Notes

- **Analyze de 2026-10-05.** C1 (crítico) corrigido: T066 protege a elegibilidade e as
  entidades. I1: FR-025 passou a ser garantia estrutural do banco. I2 e U1 foram
  corrigidos nas tasks.

- **Clarify de 2026-10-05.** Decisões registradas na spec (Clarifications), na auditoria
  (§23) e na documentação institucional (estado "especificada"). O impacto compartilhado
  da 020 na tela de conclusão está explícito, com revisão pontual da 021 FR-003 e da 014
  FR-041. As notas abaixo eram os pontos de revisão antes do clarify.

- Para revisão do solicitante antes de `/speckit-clarify` ou `/speckit-plan`, as escolhas
  E1 a E7 (já decididas), principalmente:
  - E1: sem telefone/WhatsApp, embora a nota de roadmap mencione WhatsApp;
  - E2: e-mail sem criptografia de aplicação;
  - E7: convite secundário na tela de conclusão, que revisa a 021 FR-003 de "única ação"
    para "ação principal".
