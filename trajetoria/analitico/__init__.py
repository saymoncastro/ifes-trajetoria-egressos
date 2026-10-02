"""Snapshot analítico institucional reprodutível (specs/012-dataset-analitico-reprodutivel).

Fotografia imutável de uma Campanha encerrada que entrou em coleta: congela só o que pode
derivar — pertencimento ao universo, elegibilidade no momento da captura e contexto
acadêmico da Conclusão. Campanha, Versão, Participação e Respostas já são historicamente
imutáveis depois do encerramento e são referenciadas, nunca copiadas. Sem interface.

Decisões pendentes que este app respeita:

- DP-1201: nenhum snapshot é oficial, vigente ou "o último"; toda leitura recebe o snapshot
  explicitamente.
- DP-1202: retenção e eliminação não decididas; nenhuma remoção existe, e o `PROTECT` na
  Conclusão faz qualquer eliminação futura exigir decisão explícita.
- 004/DP-408 e 005/DP-507: parcialmente resolvidas — fotografia depois do encerramento;
  Participação de Conclusão não elegível no snapshot preservada como não elegível.
- 011/DP-1101: nenhuma supressão de grupos pequenos na captura interna.
- 002/DP-006: nenhuma correspondência entre Perguntas de Versões diferentes.
- 005/DP-503, 006/DP-601, 007/DP-703: rascunhos preservados e distinguíveis; concluída por
  recusa conta como concluída; Participação sem Respostas conta como iniciada (como na 011).
"""
