# Validação — Feature 023 (jornada de resposta com menos esforço)

Registro das verificações da implementação. Dados sempre fictícios.

**Estado em 2026-10-05:** implementação concluída e validada localmente (macOS arm64,
navegador do app com viewport emulado de 375×812). Pendente: aparelho real e teste com
egressos (etapa posterior, fora desta feature).

## Verificações do CI (local)

| Verificação | Resultado |
|---|---|
| `ruff check .` | sem achados |
| `manage.py check` | sem problemas |
| `makemigrations --check --dry-run` | nenhuma migração |
| `pytest` (suíte completa) | 2 921 aprovados, 40 pulados (os de vídeo, sem renderizador) |
| Testes novos | `tests/acesso/test_pendente.py` (9), `tests/participacao/test_jornada_maximo.py` (7), `tests/interface/test_interface_esforco.py` (32) |

## Medição de rolagem — cenário A (SC-006)

Percurso da auditoria: Termos → Pessoais → Curso → Graduação → Avaliação → Trabalha →
Estudo → Seção 13 → Concluir → Concluída. Altura total da página (`scrollHeight`) ÷ 812.

| Tela | Antes (auditoria) | Depois | Observação |
|---|---:|---:|---|
| S1 Termos | 1 970 | 1 382 | convite recolhido; pergunta a 948 px (era 1 405) |
| S2 Pessoais | 2 753 | 2 647 | Sim/Não lado a lado; "(opcional)" |
| S3 Curso | 1 961 | 1 880 | |
| S6 Graduação | ~1 050 | 964 | |
| S8 Avaliação | 4 296 | 3 730 | com o ponto do meio |
| S9 Trabalha | 4 300 | 4 366 | ponto do meio (+190 px) maior que o ganho do lado a lado |
| S11 Estudo | 1 829 | 1 773 | |
| S13 | 1 687 | 1 650 | |
| Concluir | 1 393 | 1 369 | ação antes da revisão |
| Concluída | 1 123 | 1 307 / ~1 110 | com / sem próxima formação pendente |
| **Total (telas)** | **~27,6** | **~25,7** (sem próxima formação) | **meta ≤ 25 não atingida** |
| Primeira pergunta da S1 | 1,73 tela | **1,17 tela** | meta ≤ 1,4 atingida |

**Leitura honesta.** A redução foi de cerca de 1,9 tela (7%), menor que a meta. Dois
acréscimos deliberados respondem por cerca de 0,9 tela: a linha de parte em toda Seção
(FR-013) e o ponto seguro de salvamento nas duas Seções longas (FR-010). A primeira versão
do aviso "Parte anterior salva." em caixa somava mais 0,9 tela; ele foi reduzido a uma linha
junto da parte durante a validação. Atingir ≤ 25 sem tirar esses dois recursos exigiria
mexer no espaçamento entre perguntas, o que é auditoria visual, ou nas Seções do
instrumento (EF-10, nova Versão). As duas coisas estão fora desta feature.

## Code review

Revisão do diff (nível alto) com 9 achados, todos corrigidos e cobertos por teste:

- limite de tamanho do envio pendente (até 60 campos e 20 000 caracteres), para que um POST sem sessão não vire depósito no banco;
- a expiração do registro no banco continua contada do envio quando ele é marcado como apresentado (FR-004);
- envio pendente de Participação já concluída é descartado no login, em vez de desviar para a confirmação;
- a confirmação calcula "você parou em" só para a formação exibida;
- `onde_parou_da_participacao` único em `interface/apresentacao.py`;
- teste da restauração pelo declarante;
- constante sem uso removida;
- classe `opcional` no lugar de `obrigatoria`;
- mensagem "Selecione o nível de ensino." para o nível em botões de opção.

## Comportamento verificado no navegador

| Item | Resultado | Evidência |
|---|---|---|
| Parte e máximo ("Parte 1 · faltam no máximo 8 partes"; "Parte 8 · última parte") | ✓ | `evidencias/01-…` |
| Convite recolhido em "Sobre esta pesquisa", termos visíveis | ✓ | `evidencias/01-…` |
| Sim/Não lado a lado, célula inteira tocável | ✓ | `evidencias/03-…` |
| Complemento oculto até marcar "Outro:" e visível ao marcar | ✓ | `evidencias/04-…`, `05-…` |
| Ponto do meio "Precisa parar? … Salvar e sair" | ✓ | `evidencias/04-…` |
| "Parte anterior salva." discreto, junto da parte | ✓ | após o ajuste |
| Conclusão: aviso e botão antes da revisão; "Parte X" no lugar de "Seção 13" | ✓ | `evidencias/06-…` |
| Confirmação com "Você também pode responder sobre" e o botão da próxima formação | ✓ | `evidencias/07-…` |
| Formações: "Falta só concluir." para formação finalizada e não concluída | ✓ | Bruno |
| Sessão expirada → aviso, envio guardado, restauração | ✓ por testes de requisição (`test_interface_esforco.py`) | — |

## Não verificado

- Aparelho real (iOS e Android), leitor de tela e fonte ampliada do sistema.
- Navegador sem suporte a `:has()` (comportamento esperado: complemento sempre visível).
