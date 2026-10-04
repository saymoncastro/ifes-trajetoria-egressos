# ADR 0004 — Critério de Campanha é abrangência do instrumento, não foco de mobilização

- **Status**: Aceito. Decidido pelo solicitante em 2026-10-03, na revisão de produto e
  arquitetura posterior à Feature 016.
- **Data**: 2026-10-03
- **Contexto de origem**: [spec da Feature 004](../../specs/004-campanhas-populacao-elegivel/spec.md)
  (FR-015 a FR-033, FR-053), [spec da Feature 005](../../specs/005-participacao-respostas-rascunho/spec.md)
  (FR-011, FR-012), cenário de demonstração das Features 008, 011 e 016
  (`trajetoria/demonstracao/cenario.py`).

## Contexto

A 004 dá à Campanha seis critérios opcionais — ano mínimo, ano máximo, unidades, níveis,
modalidades e formas de oferta — e o contrato de admissão: uma Campanha admite nova
Participação de uma Conclusão se, e somente se, está EM COLETA e a Conclusão é ELEGÍVEL
(004 FR-053). A 005 usa esse contrato como condição de início (005 FR-011).

A prática institucional que a 004 descreve é outra: ampla divulgação e acesso espontâneo
dos egressos durante o período. Concentrar a divulgação em uma coorte ("egressos de 2023",
"Campus Serra") é estratégia de alcance, não definição de quem pode responder. A PAEG não
define coortes de resposta, e quem é egresso é definido pelo Princípio II da Constituição
(PAEG, Art. 3º), não pela Campanha.

O código já suporta essa prática: critério ausente não restringe, e uma Campanha sem
critério admite qualquer Conclusão Acadêmica em coleta. O uso, porém, derivou:

- a "coleta ampla" da demonstração tinha `ano_minimo=2015` e seis unidades; egressos de
  Vitória e de antes de 2015 viam "sem pesquisa disponível";
- a Campanha de demonstração do acompanhamento (011) era restrita a {Serra, Vitória} só
  para ser relevante à CSAEG de Vitória;
- as discussões de roadmap posteriores à 016 passaram a tratar os critérios como público de
  divulgação de uma Campanha.

Se nada mudar, a futura gestão de Campanha transformaria esses critérios em ferramenta de
segmentação de divulgação com efeito transacional: um egresso fora do foco seria recusado.

## Alternativas consideradas

- **Retirar os critérios da Campanha** — perde um uso legítimo: um instrumento que só se
  aplica a parte das formações (por exemplo, um questionário próprio da pós-graduação).
  Sem critério, duas Campanhas EM COLETA com instrumentos diferentes cobririam todas as
  Conclusões e a 007 declararia ambiguidade para todos (004 FR-051; 004/DP-404).
- **Renomear "elegibilidade" no código** — custo sem mudança de comportamento: o efeito
  transacional é correto quando o critério expressa abrangência.
- **Manter o modelo e fixar o significado** — escolhida.

## Decisão

**Critério de Campanha significa exclusivamente "esta Versão se aplica a estas
formações". A ausência de critério é o padrão. Foco de mobilização — coorte, campus, curso
ou situação de contato usados para escolher quem será abordado — não é configuração de
Campanha e nunca decide quem pode responder.**

- Na 004 e na 005, **ELEGÍVEL** significa **na abrangência da Campanha**. Não é a
  definição de egresso (Princípio II) nem pertença a uma coorte mobilizada.
- Mobilizar um grupo não exclui os demais. Uma resposta espontânea fora do foco de
  mobilização é admissível sempre que a formação estiver na abrangência da Campanha.
- O foco de mobilização pertencerá ao futuro Lote de mobilização, que registra quem foi
  abordado e não participa da admissão.

## Consequências

- Nenhuma alteração estrutural ou comportamental de modelo ou contrato: esta ADR corrige e
  explicita a semântica de uso dos critérios existentes. Não há migração; as specs 004 e 005
  recebem notas de revisão com este significado.
- Demonstração: a "coleta ampla" não tem critério; a Campanha nunca aberta do acompanhamento
  passa a se chamar "Demonstração — rodada em preparação", também sem critério; a "coleta
  sobreposta" é o único cenário com abrangência restrita (instrumento da pós-graduação de
  Vila Velha) e mantém a ambiguidade operacional da 007. Nenhuma Pessoa com Conclusão vê
  "sem pesquisa disponível" na demonstração; esse estado continua coberto pelos testes da
  007 e da 008 com dados próprios.
- Acompanhamento (011): "Elegíveis atuais" são as formações na abrangência da Campanha;
  numa Campanha sem critério, todas as Conclusões conhecidas no escopo do operador. O rótulo
  não muda agora.
- Comunicação simulada (016): o público da simulação é apenas um substituto temporário para
  exercitar a comunicação antes de existir Lote. Ele não modela nem antecipa a semântica do
  futuro Lote, que será uma seleção operacional própria, e não define quem pode responder.
- Gestão de Campanha: a interface principal não deve expor os critérios. Eles só aparecem
  quando houver instrumento com abrangência realmente restrita, com texto que impeça usá-los
  como foco de divulgação.
- Formação declarada (proposta, ainda sem decisão): depois da validação acadêmica, basta
  confirmar a condição de egresso e, se a Campanha tiver abrangência restrita, a
  compatibilidade com ela. Foco de mobilização nunca se aplica.
- Reavaliar quando o Lote de mobilização for especificado.
