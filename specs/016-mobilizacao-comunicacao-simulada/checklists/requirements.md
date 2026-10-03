# Specification Quality Checklist: Mobilização e comunicação simulada da pesquisa

**Purpose**: Validar completude e qualidade da especificação antes do planejamento.

**Created**: 2026-10-03

**Feature**: [spec.md](../spec.md)

**Marker Semantics**: `[x]` significa requisito revisado quanto à qualidade; não significa
implementação, teste executado ou aprovação institucional. Revalidado após os ajustes aprovados em 2026-10-03.

## Content Quality

- [x] Sem desenho de implementação além das fronteiras técnicas exigidas pelo solicitante.
- [x] Foco no valor para operador: alcance, mensagem, prévia, simulação e resultado.
- [x] Texto compreensível para responsáveis pelo produto; termos de transporte definidos.
- [x] Todas as seções obrigatórias do template ativo preenchidas.

## Requirement Completeness

- [x] Nenhum marcador de esclarecimento bloqueante permanece.
- [x] Requisitos testáveis e inequívocos: 38 FRs, estados, fórmulas e permissões definidos.
- [x] Critérios de sucesso mensuráveis: 10 SCs.
- [x] Critérios de sucesso descrevem resultados observáveis, sem vincular a implementação.
- [x] Cenários de aceitação definidos nas quatro histórias obrigatórias.
- [x] Bordas incluem ausência/invalidade de contato, escopo, revogação, estados, falhas e repetição.
- [x] Escopo delimitado, sem envio real nem arquitetura de produção.
- [x] Dependências, fatos do código e escolhas reversíveis identificados.

## Feature Readiness

- [x] Todos os FRs têm verificação nas histórias, matriz, SCs ou inspeção de escopo.
- [x] Histórias cobrem público, prévia, ação, caixa local, segurança e governança.
- [x] Resultados esperados permitem demonstrar mobilização sem alterar domínio existente.
- [x] Nenhuma solução técnica antecipada, salvo restrições solicitadas de backend/infraestrutura.

## Notes

- Django, SMTP local, Mailpit, `locmem`, `mail.outbox` e a opção
  `EmailMultiAlternatives` aparecem porque o usuário exigiu essas fronteiras na spec.
  Essa instrução prevalece sobre a recomendação genérica de não mencionar frameworks/APIs.
  Na spec não há desenho de módulos ou schema. Artefatos técnicos estão no plan autorizado.
- Constituição lida integralmente; features relacionadas e código fundamentam o Contexto.
  015 é baseline atual na main `0c911b5` (PR #24), sincronizada na branch 016.
- Governança da simulação é interpretação local explícita; 004/DP-406, 004/DP-407,
  privacidade/base legal e identificação produtiva continuam abertas. Não há pergunta
  bloqueante para a demonstração; envio real continua fora do escopo.
- Revisão de consistência: deduplicação após escopo, população atual, base exclusivamente
  simulada, renderer único, resultado sem garantia de entrega, transporte bloqueado antes
  de conexão e sem história persistida.
- O cenário CSAEG deve preservar os operadores existentes, inclusive B de Vitória,
  conforme a decisão da 011. Serra e Vitória em preparação já torna o cenário exercitável.
- Checklist revisa especificação; não executa testes de uma feature ainda não implementada.
- Nenhum hook before/after specify: `.specify/extensions.yml` ausente.
- Ajustes revalidados: estados, escopo antes de deduplicação, domínio exato independente
  de SMTP, modelo não editável e zero persistência.
- Mantidos 38 FRs e 10 SCs; ajustados FR-007/009/015/016/030/036/038 e SC-004/007/008.
- Sem implementação ou commit; plan aprovado e tasks autorizadas após precisões documentais.

- Precisões pré-tasks revalidadas: POST independente sem idempotência/histórico; resultado
  individual transitório e totais; sem transação SMTP/retry; público-alvo administrativo;
  CTA não torna Serra/Vitória em preparação respondível. Mantidos 38 FRs/10 SCs.

- Achados I1/I2/O1/C1 corrigidos: remetente nomeado fixo separado de destinatário simples;
  resultado interno vs projeção agregada; testes de autorização antecipados sem RED
  artificial na auditoria final; testes caplog/HTML com sentinelas antes do tratamento
  de erros. Mantidas 50 tasks pendentes, 38 FRs e 10 SCs; sem implementação.
