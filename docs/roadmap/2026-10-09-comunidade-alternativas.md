# Comunidade no Portal do Egresso — alternativas concretas

- **Data.** 2026-10-09.
- **Natureza.** Análise de produto para decisão do solicitante. **Não é spec** e nenhuma
  alternativa entra em código a partir deste documento.
- **Por que existe.** O solicitante vê o Portal como relação nos dois sentidos, com
  comunidade, pertencimento e participação. Hoje a palavra "comunidade" é vedada no Portal
  (ADR 0009, decisão 7), porque sugeria uma rede que não existe. O roadmap só prevê a
  "comunidade agregada", que depende de decisões institucionais (§6, "fora da camada
  Portal"). Este documento detalha o que "comunidade" pode ser na prática, para que a
  palavra só volte quando houver uma experiência concreta por trás dela.

## O que já foi decidido e continua valendo

- Sem comparação social nem indicadores do tipo "72 conectados", "sua turma de 2017" ou
  "geração 2008" (auditoria de 2026-10-02, §5; roadmap, tabela do mockup).
- Sem perfil público, pareamento entre pessoas ou contato direto entre egressos na S3
  (roadmap, S3, "Fica fora").
- Dado pessoal, publicação e consentimento seguem a Constituição XVI e XVII: o que não está
  definido pela instituição é `DECISÃO PENDENTE`, nunca inferido.

## Alternativas

| | O que o egresso recebe | Depende de | Decisões necessárias | Custo | Risco principal |
|---|---|---|---|---|---|
| **A. Encontros de egressos** | Convites para encontros, palestras e eventos de egressos da sua unidade ou do seu curso | **Já existe**: Oportunidade da 025, categoria "Eventos", com público por unidade e curso | Só o vocabulário: admitir "comunidade" ou "egressos" no título desse tipo de conteúdo (revisão da decisão 7) | Muito baixo | Portal vazio se as unidades não divulgarem (o mesmo risco da 025) |
| **B. Histórias de egressos** | Ler trajetórias de outros egressos do Ifes, publicadas com consentimento; e ter a própria história publicada, se quiser | **026**: a forma "contar a própria história" é a porta de entrada. Precisa de curadoria pela unidade e de um conteúdo publicado novo | Termo de publicação versionado (XVII); retirada da publicação; uso de imagem (DP-2106); quem aprova o texto; base legal de publicação | Médio: um conteúdo novo, curado, com consentimento | Exposição de dado pessoal; expectativa de publicação que não acontece |
| **C. Retratos agregados** ("comunidade agregada" do roadmap) | Saber, em números agregados, o que egressos do seu curso ou unidade fazem hoje: área de atuação, continuidade de estudos | Resultados de Campanha encerrada com snapshot (012); limiar de exibição | DP-1101 e DP-2105 (limiar); autorização para publicar; DP-2107 (dado declarado) | Médio a alto | Reidentificação em recortes pequenos; parecer comparação social |
| **D. Canais oficiais por unidade ou curso** | Saber onde estão os grupos e canais oficiais de egressos (por exemplo, a página da coordenação ou um grupo moderado pela unidade) | Um conteúdo curado simples, como a Oportunidade, mas permanente | Quais canais são oficiais e quem os modera (governança da unidade); DP-2009 se o canal for WhatsApp | Baixo no sistema; alto na operação | Canal sem moderação; o Ifes responder pelo que acontece fora do sistema |
| **E. Rede entre egressos** (diretório, conexões, mentoria entre pares) | Encontrar e falar com outros egressos | Perfil público, busca, mensagens, moderação, denúncia, segurança | Exposição de dados; moderação; base legal; responsabilidade institucional | Alto | Privacidade, moderação e o Portal virar uma rede social a manter |

## Recomendação

1. **A agora, sem código:** é a única que já existe. A mudança é de linguagem: chamar de
   encontros de egressos o que a 025 já divulga. Ela pede uma revisão pequena da decisão 7,
   para admitir "comunidade" ou "egressos" no rótulo de eventos de egressos.
2. **B depois da 026:** a contribuição "contar a própria história" é a entrada natural, e a
   unidade decide o que publica. Precisa de spec própria, com termo de publicação.
3. **D quando uma unidade tiver um canal oficial moderado:** custo baixo no sistema, mas
   depende de decisão institucional sobre canais.
4. **C só depois das decisões institucionais** que o roadmap já lista.
5. **E não agora:** é outro produto, com custo e risco que o piloto não justifica.

Em todos os casos, "comunidade" volta ao texto do Portal só junto da experiência concreta que
a sustenta, e cada alternativa entra no Checkpoint 2 (valor e reciprocidade).

## Decisão de 2026-10-09 (solicitante, demonstração)

- **Começar pela A**, encontros e eventos de egressos. A categoria "Eventos" da 025 já existe,
  mas a experiência ainda precisa de conteúdo e de operação: unidades divulgando encontros de
  egressos com regularidade. O rótulo usa "egressos", que não é vedado; a palavra
  "comunidade" continua fora até haver experiência concreta, e a ADR 0009 não muda.
- **B (histórias de egressos)** é a próxima especificação candidata, depois da 026.

## Decisões para o solicitante

- Quais alternativas seguem para spec, e em que ordem.
- Se aceita revisar a decisão 7 da ADR 0009 para a alternativa A (rótulo de encontros de
  egressos), mantendo as demais vedações.
- Para B e D, quem na instituição seria consultado (CPAEG, ACS, unidades).
