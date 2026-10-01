# Contrato: formulário da Seção e gravação pela 005

Módulos: `trajetoria/interface/formularios.py` (`FormularioDaSecao`),
`trajetoria/interface/gravacao.py` (`salvar_secao`), `trajetoria/interface/mensagens.py`.
Atende FR-032 a FR-049, FR-070, FR-073.

## Entrada

- `secao: ConteudoSecao` — a Seção da Versão aplicada (002), obtida de
  `SituacaoDaJornada.passagens`.
- `respostas: dict[UUID, Resposta]` — `SituacaoDaJornada.respostas` (005), para valores
  iniciais e comparação.
- `dados` — `request.POST`, no envio.

Nenhuma outra fonte: nem Conclusão, nem Campanha, nem outra Participação (FR-028).

## Campos

Para cada `ConteudoPergunta p` de `secao.perguntas`, em ordem, com `n = p.posicao`:

| Tipo | Campo `p<n>` | Widget | Valor limpo | Ausente quando |
|------|--------------|--------|-------------|----------------|
| `ESCOLHA_UNICA`, ≤ 10 Opções | `ChoiceField(choices=[(str(o.posicao), o.texto)])` | rádios | posição (`int`) | nada marcado |
| `ESCOLHA_UNICA`, > 10 Opções | idem, com `("", "Selecione…")` primeiro | lista suspensa | posição (`int`) | "Selecione…" |
| `ESCOLHA_MULTIPLA` | `MultipleChoiceField` | caixas de seleção | conjunto de posições | nada marcado |
| `TEXTO_CURTO` | `CharField(strip=False)` | texto de uma linha | texto exatamente como digitado | vazio ou só espaços |
| `ESCALA` | `TypedChoiceField(coerce=int, choices=inicio..fim)` | rádios | inteiro | nada marcado |

Campos auxiliares:

- `p<n>-complemento` — só se `p` tem Opção com `complemento_textual`;
  `CharField(strip=False)`; rótulo "Descreva: «<texto da Opção>»", sem os dois-pontos
  finais do texto (ex.: "Descreva: «Outro»"); ausente quando vazio ou só espaços.
- `p<n>-remover` — só para `ESCOLHA_UNICA` em rádios e `ESCALA` **não obrigatórias**,
  com ou sem Resposta gravada; `BooleanField`; rótulo "Deixar esta pergunta sem
  resposta" (research R9, revisado).

Regras comuns:

- `required=False` em todos os campos. A obrigatoriedade aparece como texto
  "(obrigatória)" no `legend`/`label` e `aria-required="true"` no controle, sem impedir o
  envio (FR-038).
- Textos (enunciado, Opções, explicativo, rótulos de escala) exatamente como no conteúdo;
  sem numeração Q (FR-033).
- Escala: descrição do grupo com os rótulos existentes — "`<inicio>` = `<rotulo_inicio>`"
  e/ou "`<fim>` = `<rotulo_fim>`"; rótulo `None` omitido (FR-033; 003/DP-301).
- `initial` vem só de `respostas`: Opção → posição; Opções → posições; texto; inteiro;
  complemento (FR-039).
- Cada Pergunta é envolvida por um elemento com `id="p<n>"` (alvo das ligações do resumo de
  erros).

## Validação de forma (antes de qualquer gravação)

| Erro | Mensagem (`mensagens.py`) |
|------|---------------------------|
| Opção inexistente / valor não listado | "Selecione uma das opções apresentadas." |
| Ponto de escala inexistente / não inteiro | "Selecione um valor da escala." |
| Complemento presente sem a Opção que o admite marcada (inclusive sem nenhuma Opção) | "Para descrever, marque a opção «<texto da Opção>»." |

É a regra de 005 FR-030 (a) apresentada antes da gravação; a interface não acrescenta
regra (FR-044). Formulário inválido → nada é gravado.

## Gravação: `salvar_secao(participacao, secao, limpos, respostas) -> ResultadoDaGravacao`

1. Lê, somente leitura, `Pergunta.objects.filter(secao_id=secao.id)` e suas `Opcao`,
   indexadas por posição (as operações da 005 recebem instâncias).
2. Para cada Pergunta, decide **no máximo uma** operação (FR-040):

   | Situação | Operação |
   |----------|----------|
   | `p<n>-remover` marcado | `remover_resposta` (se havia Resposta) |
   | valor ausente e havia Resposta | `remover_resposta` |
   | valor ausente e não havia | nenhuma |
   | valor igual ao da Resposta (mesma Opção/conjunto/texto/inteiro **e** mesmo complemento) | nenhuma |
   | valor presente e diferente | `responder_escolha_unica(p, opcao, complemento=…)` / `responder_escolha_multipla(p, opcoes, complemento=…)` / `responder_texto(p, texto)` / `responder_escala(p, inteiro)` |

3. Todas as operações num único `transaction.atomic()`. Cada `ParticipacaoRejeitada` é
   capturada por Pergunta (fora do bloco atômico interno da operação) e classificada:
   - motivos de Pergunta → `erros_por_pergunta[n]` (mensagens do data-model §4);
   - `COLETA_NAO_ADMITIDA`, `PARTICIPACAO_CONCLUIDA`, `PARTICIPACAO_INEXISTENTE` →
     `motivo_global` (interrompe as demais operações).
   Se houver qualquer erro, `transaction.set_rollback(True)`: **nenhuma** Resposta da
   submissão fica gravada; as anteriores ficam intactas (FR-045).
4. As operações são chamadas sem `agora`.

## Garantias

- **Só a 005 grava** Respostas (SC-007). A interface não chama `save`, `create`, `update`
  ou `delete` em modelos.
- **Atomicidade da submissão** (FR-045), inclusive quando a coleta encerra entre a
  primeira e a última operação.
- **Serialização com a conclusão**: o bloqueio da Participação, adquirido pela primeira
  operação, dura até o fim da transação externa (006 FR-043).
- **Idempotência prática**: reenviar a mesma Seção sem mudança não executa operação.
- **Sem valores em rastros**: mensagens e logs não contêm texto, inteiro ou complemento
  declarados (FR-085; 005 FR-059).
- **Sem regra de navegação ou obrigatoriedade**: o resultado da gravação não diz para onde
  ir; a view consulta a 006 (FR-050, FR-051).
