# ADR 0002 — Imutabilidade da Versão publicada garantida no banco

- **Status**: **Rejeitado nesta fase (adiado)**. Proposto no `/speckit-plan` da Feature
  002 e rejeitado pelo solicitante em 2026-10-01, antes da implementação.
- **Data**: 2026-10-01
- **Contexto de origem**: [plan da Feature 002](../../specs/002-pesquisa-versao-instrumento/plan.md),
  [research R8, R9](../../specs/002-pesquisa-versao-instrumento/research.md)

## Contexto

O Princípio VIII (NON-NEGOTIABLE) exige que a Versão da Pesquisa usada em coleta não seja
modificada de forma que altere a interpretação das respostas. A spec da Feature 002 vai
além: toda Versão publicada é integralmente imutável (FR-016, FR-017) e não pode ser
excluída (FR-018). A imutabilidade total é a regra operacional enquanto a DP-003 da
Feature 002 estiver aberta, e não decisão institucional definitiva.

A imutabilidade depende de outra linha (o estado da Versão), o que CHECK não expressa.

## Proposta considerada

Além das operações de domínio (`trajetoria/instrumento/operacoes.py`), gatilhos PL/pgSQL
em `versao`, `secao`, `pergunta` e `opcao` rejeitariam escrita ou remoção de Versão
publicada e de seus elementos, criação de Versão fora de RASCUNHO, volta a RASCUNHO e
referências entre Versões, inclusive para escrita fora das operações (`update()` em
lote, SQL direto).

## Decisão

**A imutabilidade de versões publicadas será inicialmente garantida pelas operações da
aplicação e protegida por testes automatizados. Triggers PostgreSQL poderão ser
reconsiderados caso surjam múltiplos escritores da base, operações externas ao domínio
da aplicação ou requisito institucional de defesa em profundidade.**

Motivos:

- o Trajetória Ifes é atualmente o único escritor legítimo da base;
- não há necessidade concreta de outros sistemas gravando nas tabelas do instrumento;
- gatilhos distribuiriam regra de domínio entre Python e PostgreSQL;
- aumentariam a complexidade de migrações e manutenção nas primeiras features;
- a Constituição exige preservação histórica, mas não exige um mecanismo específico;
- o YAGNI (Princípio XXII) recomenda adiar defesa adicional até existir risco concreto.

## Consequências

- Toda escrita no instrumento DEVE passar pelas operações de domínio. Features futuras
  (a começar pela 003) não escrevem diretamente nos modelos do app `instrumento`.
- Testes de invariante cobrem, por operação suportada, a tentativa de alterar Versão
  publicada, Seção, Pergunta e Opção, a impossibilidade de voltar a RASCUNHO e a cópia
  independente para nova Versão.
- Escrita direta no PostgreSQL ou pelo ORM fora das operações não é protegida nesta fase.
- Nenhuma dependência de PL/pgSQL; as migrações do app contêm só o esquema.
- Reavaliar este ADR se ocorrer alguma das condições da Decisão.
