# Implementation Plan: Retorno à conclusão depois de revisar

**Branch**: `claude/033-retorno-revisao` | **Date**: 2026-10-12 | **Spec**: [spec.md](spec.md)

## Summary

Só a interface da jornada muda (`trajetoria/interface`). Um marcador de revisão viaja no
endereço (`?revisao=1`) e no formulário (campo oculto `revisao`). No envio aceito com o
marcador, `_salvar` escolhe o destino pela regra do FR-004. Validação, gravação (005) e
percurso (006) não mudam. Spec e A1 a A5 aprovadas pelo solicitante em 2026-10-12.

## Decisões técnicas

| # | Decisão | Por quê |
|---|---|---|
| R1 | Marcador: `revisao=1` na query do GET e campo oculto `revisao=1` no POST. Valor diferente de `"1"` é ignorado | Lista fechada, como `aviso` e `pendencias`. Nada em sessão, banco ou navegador (FR-001) |
| R2 | Destino em revisão: função `_destino_da_revisao(participacao, jornada, passagem)` em `views.py`, que percorre `jornada.passagens` depois da Seção enviada e devolve a primeira que **pede atenção** (`not satisfeita`, ou tem Perguntas e nenhuma Resposta em `jornada.respostas`); senão, a conclusão | Lê só a jornada já recalculada depois da gravação. `jornada.respostas` inclui as inativas, o que cobre a parte que sai e volta (edge case) |
| R3 | A regra vive na interface, não em `participacao` | Muda só o destino da navegação, como "Salvar e sair". A 006 continua a única fonte do percurso e da conclusão |
| R4 | Ordem em `_salvar` sem marcador: idêntica à de hoje. Com marcador: "Salvar e sair" primeiro (como hoje), depois a pendência (`?pendencias=1&revisao=1`), depois o FR-004 | Erro e pendência reapresentam como hoje (FR-005) |
| R5 | Aviso de mudança de caminho: código `caminho` em `mensagens.AVISOS`, variante informação, aceito só com o marcador. Confirmação na conclusão: `?aviso=revisada&secao=<posição>`, mostrada só se essa Seção estiver no percurso e tiver Resposta gravada | Mesma regra de verdade da 014 FR-008 e da 023 FR-016: nunca pela simples presença do código no endereço |
| R6 | Restauração do envio pendente: o modo revisão vem de `envio.dados["revisao"]` | O envio guardado já contém todos os campos (023 FR-002); nada novo é guardado (FR-010) |
| R7 | `secao.html`: campo oculto, rótulo do botão e linha da parte por contexto (`revisao`); "Voltar à seção anterior" com `?revisao=1`. `conclusao.html`: links com `?revisao=1` e o aviso | Sem JavaScript; a ordem da conclusão (023 FR-027) não muda nesta feature |

## Constitution Check

Sem modelo, migração, persistência ou dependência nova (XXII; 023 FR-034). Instrumento
intocado: nenhuma Pergunta, Seção ou regra muda (III, VIII, XIII). Coleta, conclusão e
validações continuam na 006 (VII). Funciona sem JavaScript, alvos e foco como hoje (XX, XXI).
Spec aprovada antes do código (XXVIII); textos provisórios sob DP-801 (XXIX). Testes por
requisição para cada cenário (XXVI). **Aprovado.**

## Testes

Arquivo novo `tests/interface/test_interface_revisao.py`:

- **Baseline (Ana, "trabalha e estuda"):** US1.1 a US1.4, US2.1, US2.2 e a contagem de envios
  (SC-001, SC-002).
- **Versões de teste** (`versao_publicada_de`): Seção só de opcionais num ramo (US2.3, US2.4);
  duas Seções novas em sequência (US2.5); parte que sai e volta com Respostas antigas.
- **Erros e saídas:** erro de forma e pendência em revisão (US3.1, US3.2); envio pendente
  restaurado com o marcador (US3.3); "Salvar e sair" (US3.4); "Voltar à seção anterior"
  (US3.5).
- **Fronteiras:** Seção sem marcador igual byte a byte à de hoje, exceto o token CSRF (US4.1);
  marcador forjado no primeiro preenchimento (US4.2); marcador em Seção fora do percurso, em
  Participação concluída e com a coleta encerrada (US4.3); a confirmação na conclusão nunca
  aparece pela simples presença do código no endereço.

As suítes existentes da jornada passam sem mudar nenhuma expectativa (SC-004). A única
alteração prevista é no teste da conclusão que verifica o `href` dos links da revisão, que
passa a conter `?revisao=1`, com nota.

## Riscos

- **Testes que comparam a Seção inteira**: a igualdade sem marcador (US4.1) protege contra
  mudança acidental.
- **Parte só de opcionais já vista e deixada em branco** é reapresentada (aceito na spec).
