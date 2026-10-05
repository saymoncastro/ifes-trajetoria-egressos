# Contrato — Rotas e telas

Todas as rotas respondem 404 com a demonstração desligada (`ModoDemonstracaoMiddleware`) e
enviam `Cache-Control: no-store`. As de POST exigem CSRF; as de GET recusam outros métodos
com 405.

## Administração (acompanhamento), marcador de gate `lotes`

| Método | Rota | Capacidade | Efeito |
| --- | --- | --- | --- |
| GET | `/acompanhamento/campanhas/<campanha>/lotes/` | `pode_consultar_lotes` (e `pode_preparar_lote` para ver a prévia e o formulário) | Lista os Lotes visíveis. Com filtros na query (`unidade`, várias; `nivel`; `ano_minimo`; `ano_maximo`; `curso`), mostra a prévia. Não grava nada. |
| POST | `/acompanhamento/campanhas/<campanha>/lotes/confirmar/` | `pode_preparar_lote` | Corpo: `nome`, filtros e `confirmo_abrangencia` (exigido sem filtros no escopo institucional). Recalcula e grava. Redireciona com 303 ao detalhe. |
| GET | `/acompanhamento/campanhas/<campanha>/lotes/<lote>/` | `pode_consultar_lotes` e Lote visível | Filtros, momento, operador (rótulo), contagens por situação e situação derivada. |
| POST | `/acompanhamento/campanhas/<campanha>/lotes/<lote>/enviar/` | `pode_enviar_lote` e Lote visível | Processa até N membros `NAO_TENTADO`. Responde com 303 ao detalhe e o aviso do resultado (totais, sem endereço). |

**Recusas**, sempre por categoria fixa e sem dado pessoal:

| Status | Categoria |
| --- | --- |
| 404 | Campanha ou Lote inexistente, ou demonstração desligada |
| 403 | Sem capacidade, fora do escopo, ou filtro de unidade da CSAEG fora do escopo ou ausente |
| 409 | Campanha encerrada (confirmar ou enviar) ou não `EM_COLETA` (enviar) |
| 422 | Lote vazio, filtros inválidos, confirmação de abrangência ausente, transporte inseguro ou indisponível, origem da base indevida |
| 500 | Envio interrompido. Membros afetados ficam como resultado incerto; o aviso diz que a caixa pode conter mensagens |

**O cliente nunca define** lista, contagem, contato, destinatário, remetente ou URL.

**Retirado**: `campanhas/<campanha>/comunicacao/` e `.../comunicacao/simular/` (016).

### Detalhe da Campanha

`acompanhamento/campanha.html` troca "Comunicação simulada" por "Lotes de mobilização",
exibido a quem tem `pode_consultar_lotes`.

## Egresso

| Método | Rota | Sujeito | Efeito |
| --- | --- | --- | --- |
| GET | `/meu-email/` | Pessoa da sessão da 018 (`pessoa_em_uso`) | Formulário: um campo de e-mail, texto de finalidade provisório (DP-2003), "não será público", botões "Salvar" e "Agora não" de mesmo peso. **Não exibe contato guardado.** |
| POST | `/meu-email/` | idem | Válido: grava um registro `EGRESSO`, salvo quando o valor é igual ao último `EGRESSO`. Mostra confirmação neutra sem repetir o endereço. Inválido: 422 com a mensagem do campo e nada gravado. |

**Regras gerais**:

- Sem Pessoa na sessão, inclusive na sessão do declarante: 303 para `/acesso/`.
- Depois de salvar ou recusar, a página oferece "Ver minha trajetória no Ifes" (só se
  `narrativa.consultas.elegivel(pessoa)` for verdadeiro) e "Ver suas formações no Ifes".

### Tela de conclusão (`interface/concluida.html`)

A tela tem **impacto compartilhado** entre 014, 021 e 020.

| Ramificação | Conteúdo |
| --- | --- |
| Ancorada em Conclusão | 1º: "Ver minha trajetória no Ifes" (ação principal, 021 FR-003 revista). 2º: parágrafo secundário com o link "Quer manter seu e-mail atualizado com o Ifes?" para `/meu-email/`. |
| Declarada (019) | Sem mudança. |

Notas de revisão: 021 FR-003 ("única ação" → "ação principal") e 014 FR-041.
