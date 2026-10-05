# Validação — Feature 020 (somente demonstração)

**Data**: 2026-10-05 · **Branch**: `claude/feature-020-audit-8056d5` (sobre a `main` em
`04efabd`).

O envio real **não foi habilitado** (Gates A e B; DP-2010). Todos os dados são fictícios,
e todos os endereços estão em `example.invalid`.

## Suíte automatizada

| Verificação | Resultado |
| --- | --- |
| `uv run pytest` | 2865 passaram, 40 pulados (os mesmos da base: renderizador de vídeo da 022 indisponível localmente), 2 desmarcados (`volume`) |
| `uv run ruff check .` | Sem achados |
| `uv run python manage.py makemigrations --check --dry-run` | Sem mudanças |
| Base antes da 020 | 2760 passaram, 40 pulados |

Cobertura das validações pedidas no plan:

| Pedido | Testes |
| --- | --- |
| Concorrência entre Lotes | `tests/mobilizacao/test_concorrencia.py`: transações reais e duas threads; confirmação simultânea, envio simultâneo, restrição do banco, colisão sem gravação parcial |
| Retomada após interrupção | `tests/mobilizacao/test_retomada.py`: limite por ação e "Continuar envio"; exceção inesperada deixa resultado incerto, nunca retentado |
| Idempotência da carga | `tests/contato/test_carga.py`: mesma lista, reordenação, valor novo, lista vazia, indisponível, inválido, falha isolada no preparo |
| Isolamento em relação ao acesso | `tests/contato/test_isolamento.py`: AST; contrato acadêmico inalterado; acesso com fonte de contatos indisponível |
| Isolamento em relação à narrativa e ao vídeo | `tests/contato/test_isolamento.py`, `tests/mobilizacao/test_fronteiras.py` (AST) e `tests/narrativa/test_contato_independente.py` (página e card idênticos com e sem contato; convite ausente) |
| Elegibilidade preservada (achado C1) | `tests/mobilizacao/test_elegibilidade_preservada.py` |
| Controles de E2 (C1–C7) | `tests/mobilizacao/test_fronteiras.py` (C1, C4, C5), `tests/contato/test_vazamento.py` (C2, C3), `tests/comunicacao/test_transporte.py` (C7) |

## Roteiro manual (quickstart §4)

Ambiente:

- banco local `trajetoria_demo_020`, preparado com `preparar_demonstracao`;
- Mailpit em `127.0.0.1:1025/8025`, sem relay;
- `TRAJETORIA_LOTE_ENVIO_POR_ACAO=3`.

| # | Cenário | Observado |
| --- | --- | --- |
| 1 | Prévia (CPAEG, "coleta ampla", Serra + Vitória) | 6 formações, 5 Pessoas (Maria conta uma vez), 4 com contato, 1 sem, 0 excluídas. Nada gravado. |
| 1 | Confirmação | Lote "Serra e Vitória — 1ª onda" congelado: 5 membros, 1 sem contato, 4 não tentados. |
| 4/5 | Envio com limite 3 | 1ª ação: 3 submetidos, restou 1. "Continuar envio": 1 submetido. Situação "Envio concluído". |
| 4 | Mailpit | 4 mensagens, uma por Pessoa com contato (SIM-P-0001, 0002, 0003, 0011), remetente `trajetoria@example.invalid`; nenhuma para SIM-P-0010 (sem contato). |
| 8 | Conclusão no celular (375 px) | "Ver minha trajetória no Ifes" primeiro; o convite "Quer manter seu e-mail atualizado com o Ifes?" vem abaixo, menor. |
| 8 | `/meu-email/` | Não exibe o e-mail importado. "Salvar" e "Agora não" com o mesmo peso. Ao salvar, a confirmação não repete o endereço. A base registra `FONTE_ACADEMICA` (preservado) e depois `EGRESSO`. |

**Ajustes feitos durante a validação**:

- concordância no aviso do envio. Antes: "Restam 1 não tentados", visível em
  `020-envio-parcial-desktop.jpg`. Agora o aviso usa singular e plural, com regressão em
  `test_retomada.py`;
- campo de e-mail com a mesma altura e largura dos campos da jornada (alvo de toque de 44
  px), sem alterar a folha compartilhada.

## Evidências

- [020-previa-lote-desktop.jpg](evidencias/020-previa-lote-desktop.jpg)
- [020-envio-parcial-desktop.jpg](evidencias/020-envio-parcial-desktop.jpg)
- [020-lote-concluido-desktop.jpg](evidencias/020-lote-concluido-desktop.jpg)
- [020-conclusao-convite-mobile.jpg](evidencias/020-conclusao-convite-mobile.jpg)
- [020-meu-email-mobile.jpg](evidencias/020-meu-email-mobile.jpg)

## O que não foi validado

| Item | Situação |
| --- | --- |
| Modo real | Só validação de fronteira, por testes. Nenhuma conexão externa. |
| Celular real | Validado só por emulação de 375 px. |
| Leitor de tela | Sem verificação manual. Marcação coberta por testes. |
